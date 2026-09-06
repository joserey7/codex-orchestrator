#!/usr/bin/env python3
"""Small, offline policy helper for explicitly classified delegation choices.

This module does not inspect a task, discover runtime state, or start agents.  The
caller supplies a task class and the currently available model/effort controls.
"""

from __future__ import annotations

from typing import Any


MODES = {"economy": 2, "balanced": 3}
EFFORTS = ("none", "minimal", "low", "medium", "high", "xhigh", "max", "ultra")
MODEL_FOR_CLASS = {
    "bounded": "gpt-5.6-luna",
    "mechanical": "gpt-5.6-luna",
    "judgment": "gpt-5.6-terra",
    "difficult": "gpt-5.6-sol",
}
PARENT_CLASSES = {
    "architecture": "architecture remains a parent responsibility",
    "review_trivial": "trivial review does not need a delegate",
    "review_exceptional": "exceptional review needs a parent decision",
}


def _result(decision: str, reason: str, mode: str) -> dict[str, Any]:
    return {
        "decision": decision,
        "reason": reason,
        "mode": mode,
        "max_concurrent_delegates": MODES.get(mode),
    }


def _blocked(reason: str, mode: str) -> dict[str, Any]:
    return _result("blocked", reason, mode)


def _is_bool(value: Any) -> bool:
    return isinstance(value, bool)


def _validate_capabilities(value: Any) -> tuple[dict[str, list[str]] | None, str | None]:
    if not isinstance(value, dict):
        return None, "capabilities must be an explicit model-to-efforts dictionary"
    parsed: dict[str, list[str]] = {}
    for model, efforts in value.items():
        if not isinstance(model, str) or not model or not isinstance(efforts, list):
            return None, "capabilities must map model names to effort lists"
        if not all(isinstance(effort, str) and effort for effort in efforts):
            return None, "capability efforts must be non-empty strings"
        parsed[model] = efforts
    return parsed, None


def choose_route(
    task_class: Any,
    mode: Any = "balanced",
    *,
    useful: Any = False,
    independent: Any = False,
    redundant: Any = False,
    active_delegates: Any = 0,
    capabilities: Any = None,
    controls_available: Any = False,
    risk: Any = None,
    escalation: Any = False,
    evidence: Any = None,
) -> dict[str, Any]:
    """Return an offline parent, delegate, or blocked routing decision.

    ``capabilities`` must be a caller-supplied ``{model: [effort, ...]}`` mapping.
    ``controls_available=True`` means the caller has explicit live model, effort,
    and clean-context controls; it is never inferred by this helper.
    """
    if not isinstance(mode, str) or mode not in MODES:
        return _blocked("mode must be exactly economy or balanced", str(mode))
    if isinstance(active_delegates, bool) or not isinstance(active_delegates, int) or active_delegates < 0:
        return _blocked("active_delegates must be a non-negative integer", mode)
    if not all(_is_bool(value) for value in (useful, independent, redundant, controls_available, escalation)):
        return _blocked("useful, independent, redundant, controls_available, and escalation must be booleans", mode)
    if risk is not None and (not isinstance(risk, str) or not risk.strip()):
        return _blocked("risk must be a non-empty string when supplied", mode)
    if evidence is not None and (not isinstance(evidence, str) or not evidence.strip()):
        return _blocked("evidence must be a non-empty string when supplied", mode)
    if not isinstance(task_class, str) or task_class not in {*MODEL_FOR_CLASS, *PARENT_CLASSES}:
        return _blocked("task_class is not an explicit supported classification", mode)

    if task_class in PARENT_CLASSES:
        return _result("parent", PARENT_CLASSES[task_class], mode)
    if escalation and not evidence:
        return _blocked("escalation requires explicit non-empty evidence", mode)
    if redundant:
        return _result("parent", "redundant work stays with the parent", mode)
    if not useful or not independent:
        return _result("parent", "only useful independent work may be delegated", mode)
    if active_delegates >= MODES[mode]:
        return _result("parent", "delegate capacity reached; wait for a free slot", mode)
    if not controls_available:
        return _blocked("explicit live model, effort, and clean-context controls are required", mode)

    available, error = _validate_capabilities(capabilities)
    if error:
        return _blocked(error, mode)
    assert available is not None
    model = MODEL_FOR_CLASS[task_class]
    efforts = available.get(model)
    if efforts is None:
        return _blocked(f"{model} is not explicitly available", mode)
    if model == "gpt-5.6-luna":
        unknown = sorted(set(efforts) - set(EFFORTS))
        if unknown:
            return _blocked("Luna effort maximum is unresolvable with unknown efforts: " + ", ".join(unknown), mode)
        if not efforts:
            return _blocked("Luna has no explicitly supported effort", mode)
        effort = max(efforts, key=EFFORTS.index)
    else:
        if "high" not in efforts:
            return _blocked(f"{model} requires explicitly supported high effort", mode)
        effort = "high"

    result = _result("delegate", f"explicit {task_class} classification selects {model}", mode)
    result.update({"model": model, "effort": effort, "fork_turns": "none"})
    return result


def choose_review(risk: Any, mode: Any = "balanced", **options: Any) -> dict[str, Any]:
    """Route a bounded review risk level through :func:`choose_route`."""
    review_classes = {
        "trivial": "review_trivial",
        "low": "mechanical",
        "normal": "judgment",
        "high": "difficult",
        "exceptional": "review_exceptional",
    }
    if not isinstance(risk, str) or risk not in review_classes:
        return _blocked("risk must be trivial, low, normal, high, or exceptional", str(mode))
    options.setdefault("useful", True)
    options.setdefault("independent", True)
    return choose_route(review_classes[risk], mode, risk=risk, **options)
