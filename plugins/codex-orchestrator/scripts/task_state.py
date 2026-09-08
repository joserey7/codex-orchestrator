#!/usr/bin/env python3
"""Validate declared coordination/evidence. This is not native runtime enforcement."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

MODES = {"economy": 2, "balanced": 3}
STATUSES = {"waiting", "active", "completed", "failed", "interrupted", "blocked", "skipped"}
KINDS = {"implementation", "discovery", "correction", "review"}
RISKS = {"trivial", "low", "normal", "high", "exceptional"}


def _text(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _count(value: Any) -> bool:
    return type(value) is int and value >= 0


def _scope(value: Any) -> str | None:
    if not _text(value):
        return None
    value = value.replace("\\", "/").rstrip("/")
    parts = value.split("/")
    if not value or any(p in ("", ".", "..") for p in parts) or any(c in value for c in ":*?[]"):
        return None
    # Conservative across Windows/macOS/Linux. Scopes are files or directory trees,
    # not glob patterns; two writers to different sections still share a file.
    return value.casefold()


def _overlap(left: str, right: str) -> bool:
    return left == right or left.startswith(right + "/") or right.startswith(left + "/")


def validate_state(raw: Any, *, acceptance: bool = False) -> list[str]:
    """Return all actionable errors. Values and sources are supplied assertions.

    Revisions must identify the complete working diff, not merely HEAD when dirty.
    Budget limits are reassessment gates, never permission to ship incomplete work.
    """
    errors: list[str] = []
    if not isinstance(raw, dict):
        return ["task state must be an object"]
    required = {"schema_version", "mode", "risk", "revision", "parent", "work", "budget"}
    missing = required - raw.keys()
    if missing:
        return ["missing state fields: " + ", ".join(sorted(missing))]
    if type(raw["schema_version"]) is not int or raw["schema_version"] != 1:
        errors.append("schema_version must be 1")
    mode, risk = raw["mode"], raw["risk"]
    if not isinstance(mode, str) or mode not in MODES:
        errors.append("mode must be economy or balanced")
    if not isinstance(risk, str) or risk not in RISKS:
        errors.append("unsupported risk")
    if not _text(raw["revision"]):
        errors.append("revision must identify the accumulated diff")
    parent = raw["parent"]
    if not isinstance(parent, dict):
        return errors + ["parent must be an object"]
    for field in ("agent_id", "requested_model", "requested_effort"):
        if not _text(parent.get(field)):
            errors.append(f"parent.{field} is required")
    if parent.get("requested_model") != "gpt-6-astra":
        errors.append("Astra must be the selected parent")
    _settings_errors(parent, "parent", errors)
    work = raw["work"]
    if not isinstance(work, list) or any(not isinstance(w, dict) for w in work):
        return errors + ["work must be an array of task objects"]
    tasks: dict[str, dict[str, Any]] = {}
    scopes: dict[str, list[str]] = {}
    dependencies: dict[str, list[str]] = {}
    for w in work:
        ident = w.get("id")
        if not _text(ident) or ident in tasks:
            errors.append("work IDs must be unique non-empty strings")
            continue
        tasks[ident] = w
        status, kind = w.get("status"), w.get("kind")
        if not isinstance(status, str) or status not in STATUSES:
            errors.append(f"{ident}: invalid status")
        if not isinstance(kind, str) or kind not in KINDS:
            errors.append(f"{ident}: invalid kind")
        if type(w.get("required")) is not bool or type(w.get("read_only")) is not bool:
            errors.append(f"{ident}: required/read_only must be booleans")
        if status == "completed" and not _text(w.get("evidence")):
            errors.append(f"{ident}: completion needs evidence")
        owned = w.get("ownership")
        if not isinstance(owned, list) or not owned or any(_scope(s) is None for s in owned):
            errors.append(f"{ident}: ownership needs relative file/directory scopes, without globs")
            scopes[ident] = []
        else:
            scopes[ident] = [_scope(s) for s in owned]  # type: ignore[misc]
        deps = w.get("depends_on")
        if not isinstance(deps, list) or not all(_text(d) for d in deps):
            errors.append(f"{ident}: depends_on must be an array of IDs")
            deps = []
        dependencies[ident] = deps
        started = status in ("active", "completed", "failed", "interrupted")
        if started:
            for field in ("agent_id", "requested_model", "requested_effort", "dispatch_source"):
                if not _text(w.get(field)):
                    errors.append(f"{ident}: {field} is required after dispatch")
            _settings_errors(w, ident, errors)
        if kind == "review":
            if w.get("read_only") is not True or w.get("fresh_context") is not True:
                errors.append(f"{ident}: reviewer must be read-only in a fresh context")
            if status == "completed" and w.get("verdict") not in ("ship", "fix-first", "rethink"):
                errors.append(f"{ident}: invalid review verdict")
        if acceptance:
            if status == "active":
                errors.append(f"{ident}: an agent is still active")
            if not w.get("required") and status != "completed" and not _text(w.get("disposition")):
                errors.append(f"{ident}: optional unfinished work needs a disposition")
    for ident, deps in dependencies.items():
        for dep in deps:
            if dep not in tasks or dep == ident:
                errors.append(f"{ident}: missing/self dependency {dep}")
            elif tasks[ident].get("status") in ("active", "completed") and tasks[dep].get("status") != "completed":
                errors.append(f"{ident}: dependency {dep} has not completed")
    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(ident: str) -> None:
        if ident in visiting:
            errors.append("dependency cycle detected")
            return
        if ident in visited:
            return
        visiting.add(ident)
        for dep in dependencies.get(ident, []):
            if dep in tasks:
                visit(dep)
        visiting.remove(ident)
        visited.add(ident)

    for ident in tasks:
        visit(ident)
    active = [w for w in tasks.values() if w.get("status") == "active"]
    agent_ids = [w.get("agent_id") for w in active if _text(w.get("agent_id"))]
    if len(set(agent_ids)) != len(agent_ids):
        errors.append("one agent cannot own multiple active dispatches")
    host_limit = raw.get("host_limit")
    if host_limit is not None and not _count(host_limit):
        errors.append("host_limit must be a non-negative integer")
    cap = MODES.get(mode, 0) if isinstance(mode, str) else 0
    if _count(host_limit):
        cap = min(cap, host_limit)
    if len(active) > cap:
        errors.append("active delegates exceed mode/host capacity; wait")
    writers = [w for w in active if w.get("read_only") is False]
    for i, left in enumerate(writers):
        for right in writers[i + 1:]:
            if any(_overlap(a, b) for a in scopes[left["id"]] for b in scopes[right["id"]]):
                errors.append(f"overlapping writers: {left['id']} / {right['id']}")
    review_ids = [w.get("agent_id") for w in tasks.values()
                  if w.get("kind") == "review" and _text(w.get("agent_id"))]
    if len(set(review_ids)) != len(review_ids):
        errors.append("each fresh review needs a new agent context/ID")
    implementers = {w.get("agent_id") for w in tasks.values()
                    if w.get("read_only") is False and _text(w.get("agent_id"))}
    for w in tasks.values():
        if w.get("kind") == "review" and _text(w.get("agent_id")):
            if w["agent_id"] in implementers or w["agent_id"] == parent.get("agent_id"):
                errors.append(f"{w['id']}: reviewer cannot be parent or implementer/correction owner")
    if risk == "exceptional" and not _text(raw.get("astra_risk_decision")):
        errors.append("exceptional risk requires an explicit Astra decision")
    parent_corrections = raw.get("parent_corrections", 0)
    if not _count(parent_corrections):
        errors.append("parent_corrections must be a non-negative integer")
        parent_corrections = 0
    _budget_errors(raw["budget"], work, errors, parent_corrections)
    if acceptance:
        for w in tasks.values():
            if w.get("required") and w.get("status") != "completed":
                replacement = tasks.get(w.get("superseded_by")) if _text(w.get("superseded_by")) else None
                if (not replacement or replacement.get("status") != "completed"
                        or not _text(w.get("disposition"))):
                    errors.append(f"{w['id']}: required work is not completed or explicitly superseded")
        revision = raw["revision"]
        for field in ("diff_inspected_revision", "verified_revision", "accepted_revision"):
            if parent.get(field) != revision:
                errors.append(f"parent.{field} must match the accumulated diff revision")
        if not _text(parent.get("verification_evidence")) or not _text(parent.get("acceptance_reason")):
            errors.append("parent verification and acceptance need evidence/reason")
        reviews = [w for w in tasks.values() if w.get("kind") == "review"
                   and w.get("reviewed_revision") == revision and w.get("status") == "completed"]
        for review in reviews:
            model = review.get("requested_model")
            allowed = {"gpt-6-astra"}
            if risk in ("trivial", "low"):
                allowed |= {"gpt-5.6-luna", "gpt-5.6-terra"}
            elif risk == "normal" and mode == "balanced":
                allowed.add("gpt-5.6-terra")
            explicit_sol = (model == "gpt-5.6-sol" and review.get("override_authority") == "user"
                            and _text(review.get("override_reason")))
            if not isinstance(model, str) or (model not in allowed and not explicit_sol):
                errors.append("review capability does not meet the mode/risk baseline")
        if risk == "trivial":
            if not reviews and not _text(raw.get("review_omission_reason")):
                errors.append("trivial review omission needs a reason")
        elif not reviews or not any(w.get("verdict") == "ship" for w in reviews):
            errors.append("required fresh review must ship the current accumulated diff")
        if any(w.get("verdict") != "ship" for w in reviews):
            errors.append("current revision has unresolved review findings")
    return errors


def _settings_errors(item: dict[str, Any], label: str, errors: list[str]) -> None:
    if type(item.get("routing_proof_required")) is not bool:
        errors.append(f"{label}: routing_proof_required must be a boolean")
    for field in ("model", "effort"):
        observed = item.get("observed_" + field)
        if observed is not None:
            if not _text(observed) or not _text(item.get("settings_source")):
                errors.append(f"{label}: observed settings require a source")
            if observed != item.get("requested_" + field):
                errors.append(f"{label}: observed {field} mismatch; stop and reverify")
        elif item.get("routing_proof_required"):
            errors.append(f"{label}: required routing proof is unobservable")
        elif not _text(item.get("unconfirmed_disclosure")):
            errors.append(f"{label}: unobservable settings require disclosure, not a guarantee")


def _budget_errors(budget: Any, work: list[dict[str, Any]], errors: list[str], parent_corrections: int) -> None:
    if not isinstance(budget, dict):
        errors.append("budget must be an explicit pre-dispatch plan")
        return
    counts = {
        "dispatches": sum(w.get("status") in ("active", "completed", "failed", "interrupted") for w in work),
        "corrections": parent_corrections + sum(w.get("kind") == "correction" and w.get("status") not in ("waiting", "blocked", "skipped") for w in work),
        "reviews": sum(w.get("kind") == "review" and w.get("status") not in ("waiting", "blocked", "skipped") for w in work),
    }
    for field, count in counts.items():
        limit = budget.get(field)
        if not _count(limit):
            errors.append(f"budget.{field} must be a non-negative integer")
        elif count > limit:
            errors.append(f"budget.{field} exceeded: reassess and explicitly revise the plan, never auto-retry")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("--acceptance", action="store_true")
    args = parser.parse_args()
    try:
        raw = json.loads(args.input.read_text(encoding="utf-8"),
                         parse_constant=lambda s: (_ for _ in ()).throw(ValueError(s)))
        errors = validate_state(raw, acceptance=args.acceptance)
    except (OSError, UnicodeError, ValueError) as exc:
        errors = [str(exc)]
    print(json.dumps({"status": "invalid" if errors else "valid_declared_state", "errors": errors}))
    return 2 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
