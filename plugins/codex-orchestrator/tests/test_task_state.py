from __future__ import annotations

import importlib.util
import unittest
from copy import deepcopy
from pathlib import Path

PLUGIN = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("task_state", PLUGIN / "scripts" / "task_state.py")
assert SPEC and SPEC.loader
state = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(state)


def dispatched(ident, kind="implementation", status="completed", model="gpt-5.6-luna", effort="max", **extra):
    value = {"id": ident, "kind": kind, "status": status, "required": True,
             "read_only": kind == "review", "fresh_context": kind == "review",
             "ownership": [f"src/{ident}"], "depends_on": [], "agent_id": "agent-" + ident,
             "requested_model": model, "requested_effort": effort, "dispatch_source": "native metadata",
             "routing_proof_required": False, "unconfirmed_disclosure": "realized settings unobservable",
             "evidence": "targeted checks passed"}
    value.update(extra)
    return value


def good_state(mode="balanced", risk="normal"):
    work = [dispatched("impl")]
    if risk != "trivial":
        model = "gpt-5.6-terra" if mode == "balanced" and risk == "normal" else "gpt-6-astra"
        effort = "high" if model == "gpt-5.6-terra" else "low"
        work.append(dispatched("review", kind="review", model=model, effort=effort,
                               reviewed_revision="worktree:abc", verdict="ship", ownership=["src"]))
    return {"schema_version": 1, "mode": mode, "risk": risk, "revision": "worktree:abc",
            "parent": {"agent_id": "parent", "requested_model": "gpt-6-astra", "requested_effort": "low",
                       "routing_proof_required": False, "unconfirmed_disclosure": "runtime model/effort unobservable",
                       "diff_inspected_revision": "worktree:abc", "verified_revision": "worktree:abc",
                       "accepted_revision": "worktree:abc", "verification_evidence": "tests pass",
                       "acceptance_reason": "requirements satisfied"},
            "work": work, "budget": {"dispatches": 4, "corrections": 2, "reviews": 2},
            "parent_corrections": 0}


class TaskStateTests(unittest.TestCase):
    def errors(self, payload, acceptance=False):
        return state.validate_state(payload, acceptance=acceptance)

    def test_valid_acceptance(self):
        self.assertEqual(self.errors(good_state(), acceptance=True), [])
        payload = good_state(risk="trivial")
        payload["review_omission_reason"] = "parent verification is sufficient"
        self.assertEqual(self.errors(payload, acceptance=True), [])

    def test_current_revision_must_be_verified_and_reviewed(self):
        payload = good_state()
        payload["revision"] = "worktree:new"
        errors = " ".join(self.errors(payload, acceptance=True))
        self.assertIn("verified_revision", errors)
        self.assertIn("fresh review", errors)

    def test_review_findings_invalidate_acceptance(self):
        payload = good_state()
        payload["work"][1]["verdict"] = "fix-first"
        self.assertIn("unresolved review findings", " ".join(self.errors(payload, acceptance=True)))

    def test_required_failure_must_be_superseded(self):
        payload = good_state()
        payload["work"][0]["status"] = "failed"
        payload["work"][0]["evidence"] = "failure evidence"
        self.assertIn("required work", " ".join(self.errors(payload, acceptance=True)))
        replacement = dispatched("replacement")
        payload["work"].append(replacement)
        payload["work"][0].update(superseded_by="replacement", disposition="replacement completed")
        self.assertNotIn("required work", " ".join(self.errors(payload, acceptance=True)))

    def test_dependencies_and_cycles(self):
        payload = good_state()
        payload["work"][0]["depends_on"] = ["review"]
        payload["work"][1]["depends_on"] = ["impl"]
        self.assertIn("cycle", " ".join(self.errors(payload)))
        payload = good_state()
        payload["work"][0]["depends_on"] = ["missing"]
        self.assertIn("missing/self", " ".join(self.errors(payload)))

    def test_parallel_writer_overlap_is_rejected(self):
        payload = good_state()
        payload["work"] = [dispatched("a", status="active", ownership=["src/auth"]),
                           dispatched("b", status="active", ownership=["SRC/AUTH/token.py"])]
        self.assertIn("overlapping writers", " ".join(self.errors(payload)))
        payload["work"][1]["ownership"] = ["src/api"]
        self.assertNotIn("overlapping writers", " ".join(self.errors(payload)))

    def test_scope_traversal_and_globs_are_rejected(self):
        for scope in ("../secret", "src/*.py", "src/../secret", "C:/secret"):
            payload = good_state()
            payload["work"][0]["ownership"] = [scope]
            self.assertIn("ownership", " ".join(self.errors(payload)))

    def test_capacity_and_host_limit(self):
        payload = good_state()
        payload["work"] = [dispatched(str(i), status="active", ownership=[f"src/{i}"]) for i in range(4)]
        self.assertIn("capacity", " ".join(self.errors(payload)))
        payload["work"] = payload["work"][:2]
        payload["host_limit"] = 1
        self.assertIn("capacity", " ".join(self.errors(payload)))

    def test_observed_mismatch_and_unobservable_proof(self):
        payload = good_state()
        payload["work"][0].update(observed_model="gpt-5.6-terra", settings_source="runtime")
        self.assertIn("mismatch", " ".join(self.errors(payload)))
        payload = good_state()
        payload["work"][0].update(routing_proof_required=True, unconfirmed_disclosure=None)
        self.assertIn("unobservable", " ".join(self.errors(payload)))

    def test_budget_is_a_reassessment_gate(self):
        payload = good_state()
        payload["budget"]["dispatches"] = 1
        self.assertIn("reassess", " ".join(self.errors(payload)))
        payload = good_state()
        payload["parent_corrections"] = 3
        self.assertIn("corrections exceeded", " ".join(self.errors(payload)))

    def test_fresh_reviewer_identity(self):
        payload = good_state()
        payload["work"].append(dispatched("review2", kind="review", model="gpt-5.6-terra", effort="high",
                                          agent_id="agent-review", reviewed_revision="worktree:abc", verdict="ship"))
        self.assertIn("new agent", " ".join(self.errors(payload)))
        payload = good_state()
        payload["work"][1]["agent_id"] = "agent-impl"
        self.assertIn("implementer", " ".join(self.errors(payload)))

    def test_review_capability_matches_mode_and_risk(self):
        payload = good_state(mode="economy", risk="normal")
        payload["work"][1]["requested_model"] = "gpt-5.6-terra"
        payload["work"][1]["requested_effort"] = "high"
        self.assertIn("review capability", " ".join(self.errors(payload, acceptance=True)))
        payload["work"][1].update(requested_model="gpt-5.6-sol", requested_effort="medium",
                                   override_authority="user", override_reason="explicit experiment")
        self.assertNotIn("review capability", " ".join(self.errors(payload, acceptance=True)))

    def test_optional_unfinished_work_needs_disposition(self):
        payload = good_state()
        optional = {"id": "optional", "kind": "discovery", "status": "skipped", "required": False,
                    "read_only": True, "ownership": ["docs"], "depends_on": []}
        payload["work"].append(optional)
        self.assertIn("disposition", " ".join(self.errors(payload, acceptance=True)))
        optional["disposition"] = "not needed after direct evidence"
        self.assertNotIn("disposition", " ".join(self.errors(payload, acceptance=True)))

    def test_malformed_types_do_not_crash(self):
        payload = good_state()
        for field, value in [("mode", []), ("risk", {}), ("host_limit", True), ("parent_corrections", -1)]:
            broken = deepcopy(payload)
            broken[field] = value
            self.assertTrue(self.errors(broken))


if __name__ == "__main__":
    unittest.main()
