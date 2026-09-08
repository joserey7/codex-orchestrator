from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

PLUGIN = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("routing_policy", PLUGIN / "scripts" / "routing_policy.py")
assert SPEC and SPEC.loader
policy = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(policy)
CAPS = {policy.LUNA: ["medium", "high", "max", "ultra"], policy.TERRA: ["high"],
        policy.ASTRA: ["low", "medium"], policy.SOL: ["medium", "high"]}


class RoutingPolicyTests(unittest.TestCase):
    def route(self, task="bounded", **kwargs):
        options = dict(useful=True, independent=True, capabilities=CAPS,
                       controls_available=True, controls_source="test native schema")
        options.update(kwargs)
        return policy.choose_route(task, **options)

    def review(self, risk="normal", **kwargs):
        options = dict(capabilities=CAPS, controls_available=True, controls_source="test native schema")
        options.update(kwargs)
        return policy.choose_review(risk, **options)

    def test_economy_matrix(self):
        for task, decision, effort in [("mechanical", "delegate", "medium"), ("bounded", "delegate", "max"),
                                       ("judgment", "parent", None), ("difficult", "parent", None),
                                       ("architecture", "parent", None)]:
            with self.subTest(task=task):
                r = self.route(task, mode="economy")
                self.assertEqual((r["decision"], r.get("effort")), (decision, effort))

    def test_balanced_matrix(self):
        for task, model, effort in [("mechanical", policy.LUNA, "max"), ("bounded", policy.LUNA, "max"),
                                   ("judgment", policy.TERRA, "high"), ("difficult", policy.SOL, "medium")]:
            with self.subTest(task=task):
                r = self.route(task, rationale="bounded cross-module constraints need this capability")
                self.assertEqual((r["decision"], r["model"], r["effort"]), ("delegate", model, effort))
                self.assertFalse(r["override"])

    def test_capacity_waits_instead_of_assigning_astra(self):
        for mode, cap in policy.MODES.items():
            for count in (cap, cap + 1):
                self.assertEqual(self.route(mode=mode, active_delegates=count)["decision"], "wait")
                self.assertEqual(self.review("high", mode=mode, active_delegates=count)["decision"], "wait")

    def test_host_cap_and_mode_switch_drain(self):
        for kwargs in [dict(host_limit=1, active_delegates=1), dict(host_limit=0),
                       dict(mode="economy", active_delegates=3)]:
            self.assertEqual(self.route(**kwargs)["decision"], "wait")

    def test_serial_delegation_and_readiness_are_distinct(self):
        self.assertEqual(self.route(independent=False)["decision"], "delegate")
        self.assertEqual(self.route(independent=False, active_delegates=1)["decision"], "wait")
        self.assertEqual(self.route(ready=False)["decision"], "wait")
        self.assertEqual(self.route(delegable=False)["decision"], "parent")
        self.assertEqual(self.route("difficult", delegable=False)["decision"], "parent")

    def test_skip_never_means_parent_execution(self):
        self.assertEqual(self.route(useful=False)["decision"], "skip")
        self.assertEqual(self.route(redundant=True)["decision"], "skip")

    def test_parent_effort_is_not_modified(self):
        r = self.route("architecture")
        self.assertEqual(r["decision"], "parent")
        self.assertNotIn("effort", r)
        self.assertIn("user-selected", r["parent_effort"])

    def test_stronger_workers_need_rationale_not_a_failure(self):
        for task, model in [("judgment", policy.TERRA), ("difficult", policy.SOL)]:
            self.assertEqual(self.route(task)["decision"], "blocked")
            self.assertEqual(self.route(task, rationale="new bounded capability need")["model"], model)

    def test_exceptional_risk_cannot_silently_pass(self):
        self.assertEqual(self.route("mechanical", risk="exceptional")["decision"], "blocked")
        r = self.route("mechanical", risk="exceptional", astra_risk_decision="exact edit and scrutiny approved")
        self.assertEqual(r["model"], policy.LUNA)
        self.assertTrue(r["review_required"])
        self.assertTrue(r["astra_decision_required"])

    def test_review_matrix_is_identical_in_both_modes(self):
        expected = [("low", policy.LUNA, "max"), ("normal", policy.TERRA, "high"),
                    ("high", policy.SOL, "high"), ("exceptional", policy.ASTRA, "low")]
        for mode in policy.MODES:
            self.assertEqual(self.review("trivial", mode=mode)["decision"], "skip")
            for risk, model, effort in expected:
                with self.subTest(mode=mode, risk=risk):
                    r = self.review(risk, mode=mode, astra_risk_decision="explicit review plan")
                    self.assertEqual((r["model"], r["effort"]), (model, effort))
                    self.assertFalse(r["override"])
                    self.assertEqual(r["roles"], ["reviewer"])
                    self.assertTrue(r["read_only"] and r["fresh_context"])
        self.assertEqual(self.review("exceptional")["decision"], "blocked")

    def test_execution_mode_never_changes_high_risk_review_effort(self):
        worker = self.route("difficult", rationale="bounded difficult work")
        self.assertEqual(worker["effort"], "medium")
        self.assertEqual(self.review("high")["effort"], "high")

    def test_unavailable_route_does_not_fall_back(self):
        for kwargs in [dict(controls_available=False), dict(controls_source=None), dict(capabilities={}),
                       dict(capabilities={policy.LUNA: ["ultra"]}), dict(capabilities=[]),
                       dict(capabilities={policy.LUNA: ["max", "turbo"]})]:
            with self.subTest(kwargs=kwargs):
                self.assertEqual(self.route(**kwargs)["decision"], "blocked")
        self.assertEqual(self.route("mechanical", mode="economy", capabilities={policy.LUNA: ["max"]})["decision"], "blocked")
        self.assertEqual(self.route("difficult", rationale="difficult", capabilities={policy.LUNA: ["max"]})["decision"], "blocked")
        self.assertEqual(self.review("high", capabilities={policy.SOL: ["medium"]})["decision"], "blocked")

    def test_max_individual_excludes_ultra(self):
        r = self.route()
        self.assertEqual(r["effort"], "max")
        self.assertFalse(r["automatic_descendants"])
        for fn in (self.route, lambda **kw: self.review("low", **kw)):
            self.assertEqual(fn(capabilities={policy.LUNA: ["high", "xhigh"]})["effort"], "xhigh")

    def test_explicit_overrides_and_economy_exceptions(self):
        for task, model, effort in [("judgment", policy.TERRA, "high"), ("difficult", policy.SOL, "medium")]:
            r = self.route(task, mode="economy", rationale="capability alone is not an economy exception")
            self.assertEqual(r["decision"], "parent")
            r = self.route(task, mode="economy", economy_exception_reason="Astra: decomposition would cost more")
            self.assertEqual((r["model"], r["effort"]), (model, effort))
            r = self.route(task, mode="economy", override_model=model, override_effort=effort,
                           override_reason="explicit bounded exception", override_authority="astra")
            self.assertEqual(r["model"], model)
        self.assertEqual(self.route(override_model=policy.SOL)["decision"], "blocked")

    def test_user_luna_override_remains_possible(self):
        r = self.route(override_model=policy.LUNA, override_effort="medium",
                       override_reason="explicit experiment", override_authority="user")
        self.assertEqual(r["effort"], "medium")
        self.assertEqual(self.route(override_model=policy.LUNA, override_effort="medium",
                                   override_reason="implicit reduction", override_authority="astra")["decision"], "blocked")

    def test_astra_specialist_requires_explicit_handoff(self):
        r = self.route("difficult", override_model=policy.ASTRA, override_effort="low",
                       override_reason="independent specialist analysis is worth the extra context", override_authority="astra")
        self.assertEqual((r["model"], r["effort"]), (policy.ASTRA, "low"))

    def test_override_cannot_steal_architecture_or_enable_ultra(self):
        opts = dict(override_model=policy.ASTRA, override_effort="low", override_reason="test", override_authority="user")
        self.assertEqual(self.route("architecture", **opts)["decision"], "blocked")
        opts["override_effort"] = "ultra"
        self.assertEqual(self.route(**opts)["decision"], "blocked")

    def test_review_cannot_be_skipped_downgraded_or_combined(self):
        for kwargs in [dict(useful=False), dict(redundant=True), dict(delegable=False),
                       dict(roles=["reviewer", "tester"])]:
            self.assertEqual(self.review(**kwargs)["decision"], "blocked")
        self.assertEqual(self.review("high", override_model=policy.SOL, override_effort="medium",
                                     override_authority="user", override_reason="experiment")["decision"], "blocked")
        r = self.review("normal", override_model=policy.ASTRA, override_effort="low",
                        override_authority="astra", override_reason="independent specialist scrutiny")
        self.assertEqual(r["model"], policy.ASTRA)

    def test_roles_do_not_pin_models(self):
        for role in policy.EXECUTION_ROLES:
            for task, model in [("bounded", policy.LUNA), ("judgment", policy.TERRA), ("difficult", policy.SOL)]:
                r = self.route(task, roles=[role], rationale="required local capability")
                self.assertEqual(r["roles"], [role])
                self.assertEqual(r["model"], model)
        r = self.route(roles=["worker", "tester"])
        self.assertEqual(r["roles"], ["worker", "tester"])
        self.assertEqual(r["effective_concurrency_limit"], 3)

    def test_escalation_evidence_required(self):
        self.assertEqual(self.route(escalation=True)["decision"], "blocked")
        self.assertEqual(self.route(escalation=True, evidence="previous scope was wrong")["decision"], "delegate")

    def test_malformed_inputs(self):
        for kwargs in [dict(mode=[]), dict(risk=[]), dict(active_delegates=True), dict(host_limit=-1),
                       dict(useful="yes"), dict(ready=None), dict(rationale=" "), dict(evidence=1),
                       dict(capabilities={policy.LUNA: [True]}), dict(override_model=[]),
                       dict(roles=[]), dict(roles="worker"), dict(roles=[{}]), dict(roles=["worker", "worker"]),
                       dict(roles=["reviewer"]), dict(economy_exception_reason=True)]:
            with self.subTest(kwargs=kwargs):
                self.assertEqual(self.route(**kwargs)["decision"], "blocked")

    def test_routing_fixtures(self):
        data = json.loads((PLUGIN / "examples" / "routing-cases.json").read_text(encoding="utf-8"))
        for case in data["cases"]:
            with self.subTest(case=case["name"]):
                opts = dict(capabilities=CAPS, controls_available=True, controls_source="fixture", useful=True, independent=True)
                opts.update(case["input"])
                fn = policy.choose_review if case.get("review") else policy.choose_route
                r = fn(**opts)
                for key, value in case["expected"].items():
                    self.assertEqual(r.get(key), value)

    def test_cli_from_other_cwd_and_invalid_input(self):
        with tempfile.TemporaryDirectory(prefix="routing test ") as directory:
            p = Path(directory) / "case.json"
            for payload, flag, code in [({"risk": "normal", "mode": "economy", "capabilities": CAPS,
                                         "controls_available": True, "controls_source": "fixture"}, ["--review"], 0),
                                       ({"roles": ["worker"]}, [], 2)]:
                p.write_text(json.dumps(payload), encoding="utf-8")
                result = subprocess.run([sys.executable, "-I", str(PLUGIN / "scripts" / "routing_policy.py"), str(p), *flag],
                                        cwd=directory, capture_output=True, text=True, check=False)
                self.assertEqual(result.returncode, code, result.stderr)
                self.assertIn("decision", json.loads(result.stdout))


if __name__ == "__main__":
    unittest.main()
