#!/usr/bin/env python3
"""Offline policy checks, not a scheduler, capability detector, or model benchmark."""
from __future__ import annotations

from typing import Any

MODES = {"economy": 2, "balanced": 3}
ASTRA = "gpt-6-astra"
LUNA = "gpt-5.6-luna"
TERRA = "gpt-5.6-terra"
SOL = "gpt-5.6-sol"
# Ultra can include autonomous delegation. It is NOT an individual-effort upgrade.
INDIVIDUAL_EFFORTS = ("none", "minimal", "low", "medium", "high", "xhigh", "max")
RISKS = ("trivial", "low", "normal", "high", "exceptional")
CLASSES = ("mechanical", "bounded", "judgment", "difficult", "architecture")


def _text(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _count(value: Any) -> bool:
    return type(value) is int and value >= 0


def _result(decision: str, reason: str, mode: Any, risk: Any) -> dict[str, Any]:
    return {
        "schema_version": 2,
        "decision": decision,
        "reason": reason,
        "mode": mode if isinstance(mode, str) else "invalid",
        "max_concurrent_delegates": MODES.get(mode) if isinstance(mode, str) else None,
        "risk": risk if isinstance(risk, str) else "invalid",
        "review_required": risk != "trivial",
        "astra_decision_required": risk == "exceptional",
        "parent_effort": "user-selected; low is a recommendation, not a mutation",
    }


def choose_route(
    task_class: Any,
    mode: Any = "balanced",
    *,
    useful: Any = False,
    delegable: Any = True,
    independent: Any = False,
    ready: Any = True,
    redundant: Any = False,
    active_delegates: Any = 0,
    host_limit: Any = None,
    capabilities: Any = None,
    controls_available: Any = False,
    controls_source: Any = None,
    risk: Any = "normal",
    astra_risk_decision: Any = None,
    rationale: Any = None,
    escalation: Any = False,
    evidence: Any = None,
    delegate_difficult: Any = False,
    override_model: Any = None,
    override_effort: Any = None,
    override_reason: Any = None,
    override_authority: Any = None,
) -> dict[str, Any]:
    """Check a caller's classification. Never infer live controls or savings.

    ``independent`` means safe concurrency, not eligibility for serial delegation.
    ``ready`` means dependencies are complete. Overrides are explicit decisions,
    never silent fallbacks. Sol requires a user override; economy Terra needs a
    user/Astra authorization. The caller remains responsible for truthful evidence.
    """
    def result(decision: str, reason: str) -> dict[str, Any]:
        return _result(decision, reason, mode, risk)

    if not isinstance(mode, str) or mode not in MODES:
        return result("blocked", "mode must be economy or balanced")
    if not isinstance(task_class, str) or task_class not in CLASSES:
        return result("blocked", "unsupported task classification")
    if not isinstance(risk, str) or risk not in RISKS:
        return result("blocked", "unsupported risk")
    flags = (useful, delegable, independent, ready, redundant, controls_available,
             escalation, delegate_difficult)
    if any(type(flag) is not bool for flag in flags):
        return result("blocked", "policy flags must be booleans")
    if not _count(active_delegates) or (host_limit is not None and not _count(host_limit)):
        return result("blocked", "capacity must be a non-negative integer")
    for value in (controls_source, astra_risk_decision, rationale, evidence,
                  override_model, override_effort, override_reason, override_authority):
        if value is not None and not _text(value):
            return result("blocked", "optional evidence/settings must be non-empty strings")
    if escalation and not evidence:
        return result("blocked", "escalation requires new evidence")
    if redundant or not useful:
        return result("skip", "work is redundant or not useful; do not transfer it to Astra")
    if not ready:
        return result("wait", "dependencies are not ready")
    if risk == "exceptional" and not astra_risk_decision:
        return result("blocked", "exceptional risk requires an explicit Astra decision")
    has_override = any(value is not None for value in
                       (override_model, override_effort, override_reason, override_authority))
    if has_override:
        if (override_model not in (LUNA, TERRA, SOL, ASTRA)
                or not override_effort or not override_reason
                or override_authority not in ("user", "astra")):
            return result("blocked", "override requires model, effort, reason and authority")
        if override_model == SOL and override_authority != "user":
            return result("blocked", "Sol is an explicit user override only")
        if override_effort not in INDIVIDUAL_EFFORTS:
            return result("blocked", "override effort must be an individual effort, not Ultra")
        if override_model == LUNA and override_authority != "user":
            return result("blocked", "changing the Luna effort policy requires a user override")
    if task_class == "architecture":
        if has_override:
            return result("blocked", "an override cannot transfer architectural authority")
        return result("parent", "architecture and acceptance remain with Astra")
    if not delegable:
        return result("parent", "no useful bounded handoff; Astra retains the work")
    if task_class == "judgment" and mode == "economy" and not has_override:
        decision = result("parent", "resolve ambiguity, then reclassify as bounded only if worthwhile")
        decision["strategy"] = "decompose_or_retain; exceptional Terra needs explicit authorization"
        return decision
    if task_class == "difficult" and not delegate_difficult and not has_override:
        return result("parent", "Astra handles hard work; another Astra is not mandatory")
    if has_override:
        model, effort = override_model, override_effort
    elif task_class == "judgment":
        model, effort = TERRA, "high"
    elif task_class == "difficult":
        model, effort = ASTRA, "low"
    else:
        model = LUNA
        effort = "medium" if mode == "economy" and task_class == "mechanical" else "maximum_individual"
    if model in (TERRA, ASTRA) and not (rationale or override_reason):
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
        if set(efforts) - set(INDIVIDUAL_EFFORTS) - {"ultra"}:
            return result("blocked", "unknown effort ordering; cannot establish individual maximum")
        supported = [e for e in INDIVIDUAL_EFFORTS if e in efforts]
        if not supported:
            return result("blocked", "no supported individual reasoning effort")
        effort = supported[-1]
    elif effort not in efforts:
        return result("blocked", f"{model}/{effort} is not explicitly supported; no silent fallback")
    decision = result("delegate", override_reason or rationale or f"{mode}/{task_class} selects {model}")
    decision.update(model=model, effort=effort, fork_turns="none",
                    controls_source=controls_source, observed_settings="unconfirmed",
                    effective_concurrency_limit=cap, automatic_descendants=False,
                    override=has_override, override_authority=override_authority)
    return decision


def choose_review(risk: Any, mode: Any = "balanced", **options: Any) -> dict[str, Any]:
    """A fresh review is not parent acceptance, even when its model is Astra."""
    if not isinstance(risk, str) or risk not in RISKS:
        return _result("blocked", "unsupported review risk", mode, risk)
    if not isinstance(mode, str) or mode not in MODES:
        return _result("blocked", "mode must be economy or balanced", mode, risk)
    if risk == "trivial":
        return _result("skip", "independent review may be omitted; record parent verification and reason", mode, risk)
    options.setdefault("useful", True)
    options.setdefault("independent", True)
    if risk == "low":
        task_class = "bounded"  # Never Medium for a reviewer.
    elif risk == "normal" and mode == "balanced":
        task_class = "judgment"
    else:
        task_class = "difficult"
        options["delegate_difficult"] = True
    options.setdefault("rationale", f"fresh independent {risk}-risk review under {mode} policy")
    decision = choose_route(task_class, mode, risk=risk, **options)
    decision.update(role="reviewer", read_only=True, fresh_context=True)
    return decision


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
