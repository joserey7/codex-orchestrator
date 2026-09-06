from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import unittest
from pathlib import Path


PLUGIN = Path(__file__).resolve().parents[1]
SCRIPT = PLUGIN / "scripts" / "routing_policy.py"
EXAMPLE = PLUGIN / "examples" / "routing-cases.json"
SPEC = importlib.util.spec_from_file_location("routing_policy", SCRIPT)
assert SPEC and SPEC.loader
routing_policy = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(routing_policy)


CAPABILITIES = {
    "gpt-5.6-luna": ["low", "high", "max"],
    "gpt-5.6-terra": ["high"],
    "gpt-5.6-sol": ["high"],
}


class RoutingPolicyTests(unittest.TestCase):
    def route(self, task_class: str, **overrides: object) -> dict:
        options: dict[str, object] = {
            "useful": True,
            "independent": True,
            "capabilities": CAPABILITIES,
            "controls_available": True,
        }
        options.update(overrides)
        return routing_policy.choose_route(task_class, **options)

    def assert_delegate(self, result: dict, model: str, effort: str) -> None:
        self.assertEqual(result["decision"], "delegate")
        self.assertEqual(result["model"], model)
        self.assertEqual(result["effort"], effort)
        self.assertEqual(result["fork_turns"], "none")

    def test_mechanical_work_uses_luna_at_known_highest_effort_in_each_mode(self) -> None:
        for mode, cap in (("economy", 2), ("balanced", 3)):
            with self.subTest(mode=mode):
                result = self.route("mechanical", mode=mode)
                self.assert_delegate(result, "gpt-5.6-luna", "max")
                self.assertEqual(result["mode"], mode)
                self.assertEqual(result["max_concurrent_delegates"], cap)

    def test_judgment_and_difficult_work_select_their_direct_models(self) -> None:
        self.assert_delegate(self.route("judgment"), "gpt-5.6-terra", "high")
        self.assert_delegate(self.route("difficult"), "gpt-5.6-sol", "high")

    def test_architecture_stays_with_parent_without_needing_capabilities(self) -> None:
        result = routing_policy.choose_route("architecture")
        self.assertEqual(result["decision"], "parent")
        self.assertNotIn("model", result)

    def test_review_risk_maps_to_luna_terra_sol_or_parent(self) -> None:
        self.assertEqual(routing_policy.choose_review("trivial")["decision"], "parent")
        self.assert_delegate(
            routing_policy.choose_review(
                "low", capabilities=CAPABILITIES, controls_available=True
            ),
            "gpt-5.6-luna",
            "max",
        )
        self.assert_delegate(
            routing_policy.choose_review(
                "normal", capabilities=CAPABILITIES, controls_available=True
            ),
            "gpt-5.6-terra",
            "high",
        )
        self.assert_delegate(
            routing_policy.choose_review(
                "high", capabilities=CAPABILITIES, controls_available=True
            ),
            "gpt-5.6-sol",
            "high",
        )
        self.assertEqual(routing_policy.choose_review("exceptional")["decision"], "parent")

    def test_non_useful_redundant_or_full_capacity_work_stays_with_parent(self) -> None:
        self.assertEqual(self.route("bounded", useful=False)["decision"], "parent")
        self.assertEqual(self.route("bounded", independent=False)["decision"], "parent")
        self.assertEqual(self.route("bounded", redundant=True)["decision"], "parent")
        result = self.route("bounded", mode="economy", active_delegates=2)
        self.assertEqual(result["decision"], "parent")
        self.assertIn("capacity", result["reason"])
        for mode, cap in (("economy", 2), ("balanced", 3)):
            with self.subTest(mode=mode):
                self.assertEqual(self.route("bounded", mode=mode, active_delegates=cap - 1)["decision"], "delegate")
                self.assertEqual(self.route("bounded", mode=mode, active_delegates=cap)["decision"], "parent")
                self.assertEqual(self.route("bounded", mode=mode, active_delegates=cap + 1)["decision"], "parent")

    def test_controls_and_supported_efforts_are_required_without_fallback(self) -> None:
        self.assertEqual(self.route("mechanical", controls_available=False)["decision"], "blocked")
        self.assertEqual(self.route("mechanical", capabilities=None)["decision"], "blocked")
        self.assertEqual(
            self.route(
                "judgment",
                capabilities={"gpt-5.6-terra": ["medium"]},
            )["decision"],
            "blocked",
        )
        self.assertEqual(
            self.route(
                "mechanical",
                capabilities={"gpt-5.6-luna": ["max", "turbo"]},
            )["decision"],
            "blocked",
        )

    def test_luna_uses_the_highest_explicit_supported_effort(self) -> None:
        result = self.route(
            "bounded", capabilities={"gpt-5.6-luna": ["minimal", "xhigh"]}
        )
        self.assert_delegate(result, "gpt-5.6-luna", "xhigh")

    def test_new_information_escalation_requires_evidence_for_the_reassessed_class(self) -> None:
        self.assertEqual(self.route("difficult", escalation=True)["decision"], "blocked")
        result = self.route(
            "difficult",
            escalation=True,
            evidence="A new primary source changes the required approach.",
        )
        self.assert_delegate(result, "gpt-5.6-sol", "high")

    def test_malformed_inputs_are_blocked_safely(self) -> None:
        cases = [
            ("mechanical", {"active_delegates": -1}),
            ("mechanical", {"active_delegates": True}),
            ("mechanical", {"mode": "fast"}),
            ("unknown", {}),
            ("mechanical", {"useful": "yes"}),
            ("mechanical", {"capabilities": []}),
            ("mechanical", {"controls_available": "yes"}),
            ("mechanical", {"escalation": "yes"}),
        ]
        for task_class, options in cases:
            with self.subTest(task_class=task_class, options=options):
                result = self.route(task_class, **options)
                self.assertEqual(result["decision"], "blocked")
                self.assertIn("reason", result)

    def test_routing_case_fixture_covers_expected_decisions(self) -> None:
        fixture = json.loads(EXAMPLE.read_text(encoding="utf-8"))
        self.assertEqual(fixture["schema_version"], 1)
        for case in fixture["cases"]:
            with self.subTest(case=case["name"]):
                actual = routing_policy.choose_route(**case["input"])
                for key, expected in case["expected"].items():
                    self.assertEqual(actual.get(key), expected)

    def test_helper_imports_under_isolated_standard_library_path(self) -> None:
        program = (
            "import importlib.util, sys; "
            f"path = {str(SCRIPT)!r}; "
            "spec = importlib.util.spec_from_file_location('routing_policy_isolated', path); "
            "module = importlib.util.module_from_spec(spec); "
            "spec.loader.exec_module(module); "
            "assert not any('codex-orchestrator' in entry for entry in sys.path)"
        )
        completed = subprocess.run(
            [sys.executable, "-I", "-c", program],
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)


if __name__ == "__main__":
    unittest.main()
