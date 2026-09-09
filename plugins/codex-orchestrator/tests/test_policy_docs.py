"""Catch documented matrix/topology drift; these checks cannot prove semantic compliance."""
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
SKILL = REPO / "plugins/codex-orchestrator/skills/orchestration"


def fenced_text_after(text: str, heading: str) -> str:
    section = text[text.index(heading) + len(heading):]
    start = section.index("```text") + len("```text")
    end = section.index("```", start)
    return section[start:end]


class PolicyDocumentationTests(unittest.TestCase):
    def test_readme_and_skill_share_mode_independent_review_rows(self):
        for path in (REPO / "README.md", SKILL / "SKILL.md", SKILL / "references/routing-policy.md"):
            text = path.read_text(encoding="utf-8")
            for risk, model in (("Normal", "Terra / High"), ("High", "Sol / High"), ("Exceptional", "Astra / Low")):
                rows = [line for line in text.splitlines() if line.startswith(f"| {risk} |")]
                self.assertEqual(len(rows), 1, str(path))
                self.assertEqual(rows[0].count("|"), 3, "review should not have different mode columns")
                self.assertIn(model, rows[0])

    def test_readme_has_quick_and_detailed_topology_views(self):
        text = (REPO / "README.md").read_text(encoding="utf-8")
        for heading in ("## Model topology", "### Simplified topology", "### Detailed execution topology",
                        "## Execution roles", "### Delivery flow"):
            self.assertIn(heading, text)

        for heading in ("### Simplified topology", "### Detailed execution topology"):
            block = fenced_text_after(text, heading)
            positions = [block.index(s) for s in ("ASTRA INTEGRATION + VERIFICATION", "FRESH REVIEW", "ASTRA FINAL ACCEPTANCE")]
            self.assertEqual(positions, sorted(positions), heading)

    def test_detailed_topology_shows_execution_roles_and_review_risk(self):
        text = (REPO / "README.md").read_text(encoding="utf-8")
        block = fenced_text_after(text, "### Detailed execution topology")
        for name in ("EXPLORER", "RESEARCHER", "WORKER", "TESTER"):
            self.assertIn(name, block)
        for route in ("Luna Max", "Terra High", "Sol Medium", "Sol High", "Astra Low"):
            self.assertIn(route, block)

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
