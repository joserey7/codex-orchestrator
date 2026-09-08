#!/usr/bin/env python3
"""Offline policy checks, not a scheduler, capability detector, or benchmark."""
from __future__ import annotations

from typing import Any

MODES = {"economy": 2, "balanced": 3}
ASTRA, LUNA, TERRA, SOL = "gpt-6-astra", "gpt-5.6-luna", "gpt-5.6-terra", "gpt-5.6-sol"
INDIVIDUAL_EFFORTS = ("none", "minimal", "low", "medium", "high", "xhigh", "max")
RISKS = ("trivial", "low", "normal", "high", "exceptional")
CLASSES = ("mechanical", "bounded", "judgment", "difficult", "architecture")
EXECUTION_ROLES = ("explorer", "researcher", "worker", "tester")
# Mode-independent review baselines. These are policy choices, not benchmarks.
REVIEW_ROUTES = {
    "low": (LUNA, "maximum_individual"),
    "normal": (TERRA, "high"),
    "high": (SOL, "high"),
    "exceptional": (ASTRA, "low"),
}


def _text(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _count(value: Any) -> bool:
    return type(value) is int and value >= 0


def valid_roles(roles: Any, *, review: bool = False) -> bool:
    """Execution roles may be combined; a reviewer is always a separate context."""
    return (isinstance(roles, list) and bool(roles) and all(_text(r) for r in roles)
            and len(set(roles)) == len(roles)
            and (roles == ["reviewer"] if review else all(r in EXECUTION_ROLES for r in roles)))


def individual_max(efforts: Any) -> str | None:
    if not isinstance(efforts, list) or not all(_text(e) for e in efforts):
        return None
    if set(efforts) - set(INDIVIDUAL_EFFORTS) - {"ultra"}:
        return None
    supported = [e for e in INDIVIDUAL_EFFORTS if e in efforts]
    return supported[-1] if supported else None


def review_meets_baseline(risk: Any, model: Any, effort: Any, *,
                          supported_efforts: Any = None) -> bool:
    """Shared routing/ledger policy; stronger models still need an explicit reason.

    A ledger without capability metadata can validate literal Max, not guess a
    lower runtime maximum. Supplying supported_efforts requires an evidence source
    at the caller. Ultra is deliberately outside the individual-effort policy.
    """
    if not isinstance(risk, str) or risk not in REVIEW_ROUTES or not isinstance(model, str):
        return False
    order = (LUNA, TERRA, SOL, ASTRA)
    if model not in order or order.index(model) < order.index(REVIEW_ROUTES[risk][0]):
        return False
    if not isinstance(effort, str) or effort not in INDIVIDUAL_EFFORTS:
        return False
    if model == LUNA:
        maximum = "max" if supported_efforts is None else individual_max(supported_efforts)
        return maximum is not None and effort == maximum
    minimum = "low" if model == ASTRA else "high"
    return INDIVIDUAL_EFFORTS.index(effort) >= INDIVIDUAL_EFFORTS.index(minimum)


def _result(decision: str, reason: str, mode: Any, risk: Any) -> dict[str, Any]:
    return {"schema_version": 3, "decision": decision, "reason": reason,
            "mode": mode if isinstance(mode, str) else "invalid",
            "max_concurrent_delegates": MODES.get(mode) if isinstance(mode, str) else None,
            "risk": risk if isinstance(risk, str) else "invalid",
            "review_required": risk != "trivial", "astra_decision_required": risk == "exceptional",
            "parent_effort": "user-selected; low is a recommendation, not a mutation"}


def _choose(task_class: Any, mode: Any = "balanced", *, review: bool = False,
            roles: Any = None, useful: Any = False, delegable: Any = True,
            independent: Any = False, ready: Any = True, redundant: Any = False,
            active_delegates: Any = 0, host_limit: Any = None, capabilities: Any = None,
            controls_available: Any = False, controls_source: Any = None,
            risk: Any = "normal", astra_risk_decision: Any = None, rationale: Any = None,
            economy_exception_reason: Any = None, escalation: Any = False, evidence: Any = None,
            override_model: Any = None, override_effort: Any = None,
            override_reason: Any = None, override_authority: Any = None) -> dict[str, Any]:
    roles = (["reviewer"] if review else ["worker"]) if roles is None else roles

    def result(decision: str, reason: str) -> dict[str, Any]:
        value = _result(decision, reason, mode, risk)
        if valid_roles(roles, review=review):
            value["roles"] = list(roles)
        if review:
            value.update(role="reviewer", read_only=True, fresh_context=True)
        return value

    if not isinstance(mode, str) or mode not in MODES:
        return result("blocked", "mode must be economy or balanced")
    if not isinstance(task_class, str) or task_class not in CLASSES:
        return result("blocked", "unsupported task classification")
    if not isinstance(risk, str) or risk not in RISKS:
        return result("blocked", "unsupported risk")
    if not valid_roles(roles, review=review):
        return result("blocked", "invalid roles; execution cannot include reviewer")
    flags = (useful, delegable, independent, ready, redundant, controls_available, escalation)
    if any(type(flag) is not bool for flag in flags):
        return result("blocked", "policy flags must be booleans")
    if not _count(active_delegates) or (host_limit is not None and not _count(host_limit)):
        return result("blocked", "capacity must be a non-negative integer")
    for value in (controls_source, astra_risk_decision, rationale, economy_exception_reason,
                  evidence, override_model, override_effort, override_reason, override_authority):
        if value is not None and not _text(value):
            return result("blocked", "optional evidence/settings must be non-empty strings")
    if escalation and not evidence:
        return result("blocked", "escalation requires new evidence")
    if review and risk == "trivial":
        return result("skip", "may omit independent review after parent verification; record the reason")
    if review and (not useful or redundant or not delegable):
        return result("blocked", "required independent review cannot become skip or parent work")
    if redundant or not useful:
        return result("skip", "work is redundant or not useful; do not transfer it to Astra")
    if not ready:
        return result("wait", "dependencies are not ready")
    if risk == "exceptional" and not astra_risk_decision:
        return result("blocked", "exceptional risk requires an explicit Astra decision")
    override = any(v is not None for v in (override_model, override_effort, override_reason, override_authority))
    if override:
        if (override_model not in (LUNA, TERRA, SOL, ASTRA) or not override_effort
                or not override_reason or override_authority not in ("user", "astra")):
            return result("blocked", "override requires model, effort, reason and authority")
        if override_effort not in INDIVIDUAL_EFFORTS:
            return result("blocked", "override effort must be an individual effort, not Ultra")
        if override_model == LUNA and override_authority != "user":
            return result("blocked", "changing the Luna effort policy requires a user override")
    if not review and task_class == "architecture":
        if override:
            return result("blocked", "an override cannot transfer architectural authority")
        return result("parent", "architecture and acceptance remain with Astra")
    if not delegable:
        return result("parent", "no useful bounded handoff; Astra retains the work")
    if (not review and mode == "economy" and task_class in ("judgment", "difficult")
            and not override and not economy_exception_reason):
        decision = result("parent", "resolve/decompose or retain; exceptional Terra/Sol needs an Astra reason")
        decision["strategy"] = "decompose_or_retain; do not overspecify work merely to force Luna"
        return decision
    if override:
        model, effort = override_model, override_effort
    elif review:
        model, effort = REVIEW_ROUTES[risk]
    elif task_class in ("judgment", "difficult"):
        model, effort = (TERRA, "high") if task_class == "judgment" else (SOL, "medium")
    else:
        model = LUNA
        effort = "medium" if mode == "economy" and task_class == "mechanical" else "maximum_individual"
    reason = override_reason or rationale or economy_exception_reason
    if review and not reason:
        reason = f"fresh independent {risk}-risk review; same baseline in both modes"
    if model in (TERRA, SOL, ASTRA) and not reason:
        return result("blocked", "a stronger delegate requires a concrete capability/handoff rationale")
    cap = min(MODES[mode], host_limit) if host_limit is not None else MODES[mode]
    if active_delegates >= cap:
        return result("wait", "capacity reached; wait rather than transfer execution to Astra")
    if active_delegates and not independent:
        return result("wait", "serialize this deliverable; it is not concurrency-safe")
    if not controls_available or not controls_source:
        return result("blocked", "explicit model/effort/fresh-context controls and their source are required")
    if not isinstance(capabilities, dict):
        return result("blocked", "capabilities must be an explicit model-to-efforts dictionary")
    for name, efforts in capabilities.items():
        if not _text(name) or not isinstance(efforts, list) or not all(_text(e) for e in efforts):
            return result("blocked", "malformed capabilities")
    efforts = capabilities.get(model, [])
    if effort == "maximum_individual":
        effort = individual_max(efforts)
        if effort is None:
            return result("blocked", "cannot establish a supported individual maximum; Ultra is excluded")
    elif effort not in efforts:
        return result("blocked", f"{model}/{effort} is not explicitly supported; no silent fallback")
    if review and not review_meets_baseline(risk, model, effort, supported_efforts=efforts):
        return result("blocked", "review override cannot lower the risk baseline")
    decision = result("delegate", reason or f"{mode}/{task_class} selects {model}")
    decision.update(model=model, effort=effort, fork_turns="none", task_class=task_class,
                    controls_source=controls_source, observed_settings="unconfirmed",
                    effective_concurrency_limit=cap, automatic_descendants=False,
                    override=override, override_authority=override_authority,
                    economy_exception_reason=economy_exception_reason)
    return decision


def choose_route(task_class: Any, mode: Any = "balanced", **options: Any) -> dict[str, Any]:
    """Route caller-classified execution. Roles label responsibilities, not models.

    difficult means difficult *bounded* work. Use delegable=False or architecture
    for unbounded/architectural work. independent is parallel safety; ready is
    dependency readiness. An economy Terra/Sol lane needs economy_exception_reason
    or a complete explicit override. Astra remains the parent at the chosen effort.
    """
    return _choose(task_class, mode, review=False, **options)


def choose_review(risk: Any, mode: Any = "balanced", **options: Any) -> dict[str, Any]:
    """Risk chooses the reviewer; mode only affects concurrency, never capability."""
    options.setdefault("useful", True)
    options.setdefault("independent", True)
    return _choose("bounded", mode, review=True, risk=risk, **options)


def main() -> int:
    import argparse
    import json
    from pathlib import Path
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="JSON arguments for choose_route or choose_review")
    parser.add_argument("--review", action="store_true")
    args = parser.parse_args()
    try:
        payload = json.loads(args.input.read_text(encoding="utf-8"),
                             parse_constant=lambda s: (_ for _ in ()).throw(ValueError(s)))
        if not isinstance(payload, dict):
            raise ValueError("input must be an argument object")
        decision = (choose_review if args.review else choose_route)(**payload)
    except (OSError, UnicodeError, ValueError, TypeError) as exc:
        decision = _result("blocked", str(exc), "invalid", "normal")
    print(json.dumps(decision))
    return 2 if decision["decision"] == "blocked" else 0


if __name__ == "__main__":
    raise SystemExit(main())
