from __future__ import annotations

import importlib.util
import json
import unittest
from pathlib import Path

PLUGIN = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("routing_policy", PLUGIN / "scripts" / "routing_policy.py")
assert SPEC and SPEC.loader
policy = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(policy)
CAPS = {policy.LUNA: ["medium", "high", "max", "ultra"],
        policy.TERRA: ["high"], policy.ASTRA: ["low", "medium"], policy.SOL: ["medium", "high"]}


class RoutingPolicyTests(unittest.TestCase):
    def route(self, task="bounded", **kwargs):
        options = dict(useful=True, independent=True, capabilities=CAPS,
                       controls_available=True, controls_source="test native schema")
        options.update(kwargs)
        return policy.choose_route(task, **options)

    def review(self, risk="normal", **kwargs):
        options = dict(capabilities=CAPS, controls_available=True,
                       controls_source="test native schema")
        options.update(kwargs)
        return policy.choose_review(risk, **options)

    def test_economy_matrix(self):
        for task, decision, effort in [("mechanical", "delegate", "medium"),
                                       ("bounded", "delegate", "max"),
                                       ("judgment", "parent", None),
                                       ("difficult", "parent", None),
                                       ("architecture", "parent", None)]:
            with self.subTest(task=task):
                r = self.route(task, mode="economy")
                self.assertEqual(r["decision"], decision)
                self.assertEqual(r.get("effort"), effort)

    def test_balanced_matrix(self):
        for task, model, effort in [("mechanical", policy.LUNA, "max"),
                                   ("bounded", policy.LUNA, "max"),
                                   ("judgment", policy.TERRA, "high")]:
            r = self.route(task, rationale="requires module-level engineering judgment")
            self.assertEqual((r["decision"], r["model"], r["effort"]), ("delegate", model, effort))

    def test_capacity_waits_instead_of_assigning_astra(self):
        for mode, cap in policy.MODES.items():
            for count in (cap, cap + 1):
                self.assertEqual(self.route(mode=mode, active_delegates=count)["decision"], "wait")
                self.assertEqual(self.review("high", mode=mode, active_delegates=count)["decision"], "wait")

    def test_host_cap_and_mode_switch_drain(self):
        self.assertEqual(self.route(host_limit=1, active_delegates=1)["decision"], "wait")
        self.assertEqual(self.route(host_limit=0)["decision"], "wait")
        self.assertEqual(self.route(mode="economy", active_delegates=3)["decision"], "wait")

    def test_serial_delegation_and_readiness_are_distinct(self):
        self.assertEqual(self.route(independent=False)["decision"], "delegate")
        self.assertEqual(self.route(independent=False, active_delegates=1)["decision"], "wait")
        self.assertEqual(self.route(ready=False)["decision"], "wait")
        self.assertEqual(self.route(delegable=False)["decision"], "parent")

    def test_skip_never_means_parent_execution(self):
        self.assertEqual(self.route(useful=False)["decision"], "skip")
        self.assertEqual(self.route(redundant=True)["decision"], "skip")

    def test_parent_effort_is_not_modified(self):
        r = self.route("architecture")
        self.assertEqual(r["decision"], "parent")
        self.assertNotIn("effort", r)
        self.assertIn("user-selected", r["parent_effort"])

    def test_difficult_delegation_requires_rationale(self):
        self.assertEqual(self.route("difficult", delegate_difficult=True)["decision"], "blocked")
        r = self.route("difficult", delegate_difficult=True, rationale="independent deep investigation")
        self.assertEqual((r["model"], r["effort"]), (policy.ASTRA, "low"))

    def test_terra_requires_reason_not_a_luna_failure(self):
        self.assertEqual(self.route("judgment")["decision"], "blocked")
        self.assertEqual(self.route("judgment", rationale="unresolved local tradeoff")["model"], policy.TERRA)

    def test_exceptional_risk_cannot_silently_pass(self):
        self.assertEqual(self.route("mechanical", risk="exceptional")["decision"], "blocked")
        r = self.route("mechanical", risk="exceptional", astra_risk_decision="Astra approved exact edit and review plan")
        self.assertEqual(r["model"], policy.LUNA)
        self.assertTrue(r["review_required"])
        self.assertTrue(r["astra_decision_required"])

    def test_risk_review_matrix(self):
        expected = {"economy": [("low", policy.LUNA), ("normal", policy.ASTRA), ("high", policy.ASTRA)],
                    "balanced": [("low", policy.LUNA), ("normal", policy.TERRA), ("high", policy.ASTRA)]}
        for mode, cases in expected.items():
            self.assertEqual(self.review("trivial", mode=mode)["decision"], "skip")
            for risk, model in cases:
                r = self.review(risk, mode=mode)
                self.assertEqual(r["model"], model)
                self.assertTrue(r["read_only"])
                self.assertTrue(r["fresh_context"])
        self.assertEqual(self.review("exceptional")["decision"], "blocked")
        self.assertEqual(self.review("exceptional", astra_risk_decision="additional scrutiny approved")["model"], policy.ASTRA)

    def test_unavailable_route_does_not_fall_back(self):
        for kwargs in [dict(controls_available=False), dict(controls_source=None), dict(capabilities={}),
                       dict(capabilities={policy.LUNA: ["ultra"]}), dict(capabilities=[]),
                       dict(capabilities={policy.LUNA: ["max", "turbo"]})]:
            with self.subTest(kwargs=kwargs):
                self.assertEqual(self.route(**kwargs)["decision"], "blocked")
        self.assertEqual(self.route("mechanical", mode="economy", capabilities={policy.LUNA: ["max"]})["decision"], "blocked")

    def test_max_individual_excludes_ultra(self):
        r = self.route()
        self.assertEqual(r["effort"], "max")
        self.assertFalse(r["automatic_descendants"])
        self.assertEqual(self.route(capabilities={policy.LUNA: ["high", "xhigh"]})["effort"], "xhigh")

    def test_explicit_sol_override_only(self):
        options = dict(override_model=policy.SOL, override_effort="medium", override_reason="user comparison")
        self.assertEqual(self.route(**options, override_authority="astra")["decision"], "blocked")
        self.assertEqual(self.route(**options, override_authority="user")["model"], policy.SOL)
        self.assertEqual(self.route(override_model=policy.SOL)["decision"], "blocked")

    def test_economy_terra_exception_and_user_effort_override(self):
        r = self.route("judgment", mode="economy", override_model=policy.TERRA, override_effort="high",
                       override_reason="decomposition would cost more than a bounded Terra handoff", override_authority="astra")
        self.assertEqual(r["model"], policy.TERRA)
        self.assertTrue(r["override"])
        r = self.route(override_model=policy.LUNA, override_effort="medium",
                       override_reason="explicit experiment", override_authority="user")
        self.assertEqual(r["effort"], "medium")

    def test_override_cannot_steal_architecture_or_enable_ultra(self):
        opts = dict(override_model=policy.ASTRA, override_effort="low", override_reason="test", override_authority="user")
        self.assertEqual(self.route("architecture", **opts)["decision"], "blocked")
        opts["override_effort"] = "ultra"
        self.assertEqual(self.route(**opts)["decision"], "blocked")

    def test_escalation_evidence_required(self):
        self.assertEqual(self.route(escalation=True)["decision"], "blocked")
        self.assertEqual(self.route(escalation=True, evidence="previous scope was wrong")["decision"], "delegate")

    def test_malformed_inputs(self):
        for kwargs in [dict(mode=[]), dict(risk=[]), dict(active_delegates=True), dict(host_limit=-1),
                       dict(useful="yes"), dict(ready=None), dict(rationale=" "), dict(evidence=1),
                       dict(capabilities={policy.LUNA: [True]}), dict(override_model=[])]:
            with self.subTest(kwargs=kwargs):
                self.assertEqual(self.route(**kwargs)["decision"], "blocked")

    def test_routing_fixtures(self):
        data = json.loads((PLUGIN / "examples" / "routing-cases.json").read_text(encoding="utf-8"))
        for case in data["cases"]:
            with self.subTest(case=case["name"]):
                opts = dict(capabilities=CAPS, controls_available=True, controls_source="fixture", useful=True, independent=True)
                opts.update(case["input"])
                r = policy.choose_route(**opts)
                for key, value in case["expected"].items():
                    self.assertEqual(r.get(key), value)


if __name__ == "__main__":
    unittest.main()
