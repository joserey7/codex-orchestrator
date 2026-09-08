from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from copy import deepcopy
from pathlib import Path

PLUGIN = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("task_state", PLUGIN / "scripts" / "task_state.py")
assert SPEC and SPEC.loader
state = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(state)


def dispatched(ident, kind="implementation", status="completed", model="gpt-5.6-luna", effort="max", **extra):
    value = {"id": ident, "kind": kind, "roles": [state.DEFAULT_ROLES[kind]],
             "status": status, "required": True, "read_only": kind in ("review", "discovery", "research"),
             "fresh_context": kind == "review", "ownership": [f"src/{ident}"], "depends_on": [],
             "agent_id": "agent-" + ident, "requested_model": model, "requested_effort": effort,
             "dispatch_source": "native metadata", "routing_proof_required": False,
             "unconfirmed_disclosure": "realized settings unobservable", "evidence": "targeted checks passed"}
    if kind == "review":
        value.update(parent_verified_revision="worktree:abc", parent_verification_evidence="parent checks before dispatch",
                     reviewed_revision="worktree:abc", verdict="ship")
    value.update(extra)
    return value


def good_state(mode="balanced", risk="normal"):
    work = [dispatched("impl")]
    if risk != "trivial":
        model, effort = {"low": ("gpt-5.6-luna", "max"), "normal": ("gpt-5.6-terra", "high"),
                         "high": ("gpt-5.6-sol", "high"), "exceptional": ("gpt-6-astra", "low")}[risk]
        work.append(dispatched("review", kind="review", model=model, effort=effort, ownership=["src"]))
    return {"schema_version": 1, "mode": mode, "risk": risk, "revision": "worktree:abc",
            "parent": {"agent_id": "parent", "requested_model": "gpt-6-astra", "requested_effort": "low",
                       "routing_proof_required": False, "unconfirmed_disclosure": "runtime model/effort unobservable",
                       "diff_inspected_revision": "worktree:abc", "verified_revision": "worktree:abc",
                       "accepted_revision": "worktree:abc", "verification_evidence": "tests pass",
                       "acceptance_reason": "requirements satisfied"},
            "work": work, "budget": {"dispatches": 6, "corrections": 2, "reviews": 2},
            "parent_corrections": 0, "astra_risk_decision": "explicit scrutiny plan",
            "review_omission_reason": "parent verification sufficient for trivial work"}


class TaskStateTests(unittest.TestCase):
    def errors(self, payload, acceptance=False):
        return state.validate_state(payload, acceptance=acceptance)

    def test_valid_acceptance_and_mode_independent_review(self):
        for mode in ("economy", "balanced"):
            for risk in ("trivial", "low", "normal", "high", "exceptional"):
                with self.subTest(mode=mode, risk=risk):
                    self.assertEqual(self.errors(good_state(mode, risk), acceptance=True), [])

    def test_current_revision_must_be_verified_and_reviewed(self):
        p = good_state()
        p["revision"] = "worktree:new"
        errors = " ".join(self.errors(p, acceptance=True))
        self.assertIn("verified_revision", errors)
        self.assertIn("fresh review", errors)

    def test_review_findings_invalidate_acceptance(self):
        p = good_state()
        p["work"][1]["verdict"] = "fix-first"
        self.assertIn("unresolved review findings", " ".join(self.errors(p, acceptance=True)))

    def test_required_failure_must_be_superseded(self):
        p = good_state()
        p["work"][0].update(status="failed", evidence="failure evidence")
        self.assertIn("required work", " ".join(self.errors(p, acceptance=True)))
        p["work"].append(dispatched("replacement"))
        p["work"][0].update(superseded_by="replacement", disposition="replacement completed")
        self.assertNotIn("required work", " ".join(self.errors(p, acceptance=True)))

    def test_dependencies_and_cycles(self):
        p = good_state()
        p["work"][0]["depends_on"] = ["review"]
        p["work"][1]["depends_on"] = ["impl"]
        self.assertIn("cycle", " ".join(self.errors(p)))
        p["work"][0]["depends_on"] = ["missing"]
        self.assertIn("missing/self", " ".join(self.errors(p)))
        p = good_state()
        p["work"][0]["status"] = "waiting"
        p["work"][1]["depends_on"] = ["impl"]
        self.assertIn("has not completed", " ".join(self.errors(p)))

    def test_parallel_writer_overlap_is_rejected(self):
        p = good_state()
        p["work"] = [dispatched("a", status="active", ownership=["src/auth"]),
                     dispatched("b", status="active", ownership=["SRC/AUTH/token.py"])]
        self.assertIn("overlapping writers", " ".join(self.errors(p)))
        p["work"][1]["ownership"] = ["src/api"]
        self.assertNotIn("overlapping writers", " ".join(self.errors(p)))

    def test_scope_traversal_and_globs_are_rejected(self):
        for scope in ("../secret", "src/*.py", "src/../secret", "C:/secret"):
            p = good_state()
            p["work"][0]["ownership"] = [scope]
            self.assertIn("ownership", " ".join(self.errors(p)))

    def test_capacity_and_host_limit(self):
        p = good_state()
        p["work"] = [dispatched(str(i), status="active") for i in range(4)]
        self.assertIn("capacity", " ".join(self.errors(p)))
        p["work"] = p["work"][:2]
        p["host_limit"] = 1
        self.assertIn("capacity", " ".join(self.errors(p)))

    def test_observed_mismatch_and_unobservable_proof(self):
        p = good_state()
        p["work"][0].update(observed_model="gpt-5.6-terra", settings_source="runtime")
        self.assertIn("mismatch", " ".join(self.errors(p)))
        p = good_state()
        p["work"][0].update(routing_proof_required=True, unconfirmed_disclosure=None)
        self.assertIn("unobservable", " ".join(self.errors(p)))

    def test_budget_is_a_reassessment_gate(self):
        p = good_state()
        p["budget"]["dispatches"] = 1
        self.assertIn("reassess", " ".join(self.errors(p)))
        p = good_state()
        p["parent_corrections"] = 3
        self.assertIn("corrections exceeded", " ".join(self.errors(p)))

    def test_fresh_reviewer_identity(self):
        p = good_state()
        p["work"].append(dispatched("review2", kind="review", model="gpt-5.6-terra", effort="high", agent_id="agent-review"))
        self.assertIn("new agent", " ".join(self.errors(p)))
        p = good_state()
        p["work"][1]["agent_id"] = "agent-impl"
        self.assertIn("implementer", " ".join(self.errors(p)))

    def test_review_cannot_lower_risk_baseline_even_with_override(self):
        for mode in ("economy", "balanced"):
            for risk, model, effort in [("normal", "gpt-5.6-luna", "max"), ("high", "gpt-5.6-sol", "medium"),
                                       ("exceptional", "gpt-5.6-sol", "high")]:
                p = good_state(mode, risk)
                p["work"][1].update(requested_model=model, requested_effort=effort,
                                     override_authority="user", override_reason="experiment")
                self.assertIn("risk baseline", " ".join(self.errors(p, acceptance=True)))

    def test_stronger_review_is_explicit_and_not_automatic(self):
        p = good_state()
        p["work"][1].update(requested_model="gpt-6-astra", requested_effort="low")
        self.assertIn("override reason", " ".join(self.errors(p, acceptance=True)))
        p["work"][1].update(override_authority="astra", override_reason="independent specialist scrutiny")
        self.assertEqual(self.errors(p, acceptance=True), [])

    def test_optional_unfinished_work_needs_disposition(self):
        p = good_state()
        optional = {"id": "optional", "kind": "discovery", "status": "skipped", "required": False,
                    "read_only": True, "ownership": ["docs"], "depends_on": []}
        p["work"].append(optional)
        self.assertIn("disposition", " ".join(self.errors(p, acceptance=True)))
        optional["disposition"] = "not needed after direct evidence"
        self.assertNotIn("disposition", " ".join(self.errors(p, acceptance=True)))

    def test_malformed_types_do_not_crash(self):
        for field, value in [("mode", []), ("risk", {}), ("host_limit", True), ("parent_corrections", -1)]:
            p = good_state()
            p[field] = value
            self.assertTrue(self.errors(p))
        for roles in ([], "worker", [{}], ["unknown"], ["worker", "worker"]):
            p = good_state()
            p["work"][0]["roles"] = roles
            self.assertIn("invalid roles", " ".join(self.errors(p)))

    def test_combined_worker_tester_is_one_dispatch_not_a_review(self):
        p = good_state()
        p["work"][0]["roles"] = ["worker", "tester"]
        p["budget"]["dispatches"] = 2
        self.assertEqual(self.errors(p, acceptance=True), [])
        p["work"] = p["work"][:1]
        self.assertIn("required fresh review", " ".join(self.errors(p, acceptance=True)))

    def test_reviewer_cannot_be_combined_with_execution(self):
        for roles in (["worker", "reviewer"], ["tester", "reviewer"]):
            p = good_state()
            p["work"][1]["roles"] = roles
            self.assertIn("invalid roles", " ".join(self.errors(p)))

    def test_tester_context_is_not_a_fresh_reviewer(self):
        p = good_state()
        p["work"].insert(1, dispatched("tests", kind="validation", read_only=True, agent_id="agent-tests"))
        p["work"][-1]["agent_id"] = "agent-tests"
        self.assertIn("tester", " ".join(self.errors(p)))

    def test_research_and_validation_are_execution_kinds(self):
        p = good_state()
        p["work"].insert(0, dispatched("discovery", kind="discovery"))
        p["work"].insert(1, dispatched("research", kind="research"))
        p["work"].insert(3, dispatched("tests", kind="validation", read_only=True))
        self.assertEqual(self.errors(p, acceptance=True), [])
        p["work"][1]["read_only"] = False
        self.assertIn("read-only", " ".join(self.errors(p)))

    def test_kind_and_role_must_agree_but_legacy_roles_are_optional(self):
        p = good_state()
        p["work"][0]["roles"] = ["tester"]
        self.assertIn("kind must agree", " ".join(self.errors(p)))
        for w in p["work"]:
            w.pop("roles", None)
        self.assertEqual(self.errors(p, acceptance=True), [])

    def test_review_requires_parent_verification_before_dispatch(self):
        for field in ("parent_verified_revision", "parent_verification_evidence"):
            p = good_state()
            p["work"][1].pop(field)
            self.assertIn("before dispatch", " ".join(self.errors(p, acceptance=True)))
        p = good_state()
        p["work"][1]["status"] = "active"
        p["parent"]["verified_revision"] = "worktree:old"
        self.assertIn("Astra verification", " ".join(self.errors(p)))

    def test_active_review_requires_stable_candidate(self):
        p = good_state()
        p["work"][1]["status"] = "active"
        self.assertEqual(self.errors(p), [])
        p["work"][0]["status"] = "active"
        self.assertIn("writers are active", " ".join(self.errors(p)))

    def test_correction_requires_new_verification_and_fresh_review(self):
        p = good_state()
        p["work"][1]["verdict"] = "fix-first"
        p["revision"] = "worktree:fixed"
        p["work"].append(dispatched("fix", kind="correction"))
        p["parent"].update(diff_inspected_revision=p["revision"], verified_revision=p["revision"], accepted_revision=p["revision"])
        self.assertIn("required fresh review", " ".join(self.errors(p, acceptance=True)))
        p["work"].append(dispatched("review2", kind="review", model="gpt-5.6-terra", effort="high",
                                     parent_verified_revision=p["revision"], reviewed_revision=p["revision"]))
        self.assertEqual(self.errors(p, acceptance=True), [])

    def test_runtime_luna_max_needs_capability_evidence_when_below_literal_max(self):
        p = good_state(risk="low")
        p["work"][1]["requested_effort"] = "xhigh"
        self.assertIn("risk baseline", " ".join(self.errors(p, acceptance=True)))
        p["work"][1].update(supported_efforts=["high", "xhigh"], capabilities_source="live schema")
        self.assertEqual(self.errors(p, acceptance=True), [])
        p["work"][1]["supported_efforts"] = ["high", "xhigh", "max"]
        self.assertIn("risk baseline", " ".join(self.errors(p, acceptance=True)))

    def test_examples_validate_and_cli_is_portable(self):
        example = PLUGIN / "examples" / "task-state.json"
        p = json.loads(example.read_text(encoding="utf-8"))
        self.assertEqual(self.errors(p, acceptance=True), [])
        with tempfile.TemporaryDirectory(prefix="task state ") as directory:
            result = subprocess.run([sys.executable, "-I", str(PLUGIN / "scripts" / "task_state.py"), str(example), "--acceptance"],
                                    cwd=directory, capture_output=True, text=True, check=False)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(json.loads(result.stdout)["status"], "valid_declared_state")


if __name__ == "__main__":
    unittest.main()
