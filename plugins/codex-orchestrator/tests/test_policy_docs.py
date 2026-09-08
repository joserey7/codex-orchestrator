"""Catch documented matrix drift; these checks cannot prove semantic compliance."""
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
SKILL = REPO / "plugins/codex-orchestrator/skills/orchestration"


class PolicyDocumentationTests(unittest.TestCase):
    def test_readme_and_skill_share_mode_independent_review_rows(self):
        for path in (REPO / "README.md", SKILL / "SKILL.md", SKILL / "references/routing-policy.md"):
            text = path.read_text(encoding="utf-8")
            for risk, model in (("Normal", "Terra / High"), ("High", "Sol / High"), ("Exceptional", "Astra / Low")):
                rows = [line for line in text.splitlines() if line.startswith(f"| {risk} |")]
                self.assertEqual(len(rows), 1, str(path))
                self.assertEqual(rows[0].count("|"), 3, "review should not have different mode columns")
                self.assertIn(model, rows[0])

    def test_readme_topology_puts_review_between_verification_and_acceptance(self):
        text = (REPO / "README.md").read_text(encoding="utf-8")
        positions = [text.index(s) for s in ("ASTRA INTEGRATION + VERIFICATION", "FRESH REVIEW", "ASTRA FINAL ACCEPTANCE")]
        self.assertEqual(positions, sorted(positions))
        for heading in ("## Model topology", "## Execution roles", "### Delivery flow"):
            self.assertIn(heading, text)

    def test_logical_roles_and_combination_are_documented(self):
        for path in (REPO / "README.md", SKILL / "SKILL.md"):
            text = path.read_text(encoding="utf-8")
            for name in ("Explorer", "Researcher", "Worker", "Tester", "Reviewer", "Worker + Tester"):
                self.assertIn(name, text)

    def test_both_worker_and_review_sol_efforts_are_documented(self):
        for path in (REPO / "README.md", SKILL / "SKILL.md", SKILL / "references/routing-policy.md"):
            text = path.read_text(encoding="utf-8")
            self.assertIn("Sol / Medium", text)
            self.assertIn("Sol / High", text)


if __name__ == "__main__":
    unittest.main()
