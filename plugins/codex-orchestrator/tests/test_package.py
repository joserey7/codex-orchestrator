from __future__ import annotations

import importlib.util
import io
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from urllib.parse import urlsplit


REPO = Path(__file__).resolve().parents[3]
PACKAGE = REPO / "plugins" / "codex-orchestrator"
VERIFY = PACKAGE / "scripts" / "verify.py"
MANIFEST = PACKAGE / ".codex-plugin" / "plugin.json"


def load_verifier():
    spec = importlib.util.spec_from_file_location("package_verify", VERIFY)
    if spec is None or spec.loader is None:
        raise AssertionError(f"cannot import verifier: {VERIFY}")
    module = importlib.util.module_from_spec(spec)
    with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
        spec.loader.exec_module(module)
    return module


verifier = load_verifier()


class PackageVerificationTests(unittest.TestCase):
    def copy_repo(self, parent: Path) -> Path:
        destination = parent / "repository copy with spaces"
        shutil.copytree(
            REPO,
            destination,
            ignore=shutil.ignore_patterns(".git", "__pycache__"),
        )
        return destination

    def validation_errors(self, repo: Path) -> list[str]:
        return verifier.validate_package(repo)

    def test_repository_passes_structural_validation(self) -> None:
        self.assertEqual(self.validation_errors(REPO), [])

    def test_all_markdown_links_resolve_inside_repository(self) -> None:
        root = REPO.resolve()
        for path in sorted(REPO.rglob("*.md")):
            if ".git" in path.parts:
                continue
            for target in verifier.markdown_links(path.read_text(encoding="utf-8")):
                parsed = urlsplit(target)
                if parsed.scheme or parsed.netloc or target.startswith("#"):
                    continue
                resolved = (path.parent / parsed.path).resolve()
                self.assertTrue(
                    resolved.is_relative_to(root),
                    f"{path.relative_to(REPO)} link escapes repository: {target}",
                )
                self.assertTrue(
                    resolved.is_file(),
                    f"{path.relative_to(REPO)} link is missing: {target}",
                )

    def test_manifest_and_examples_use_codex_orchestrator_identity(self) -> None:
        manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        self.assertEqual(manifest["name"], "codex-orchestrator")
        self.assertEqual(manifest["version"], "0.3.0")
        self.assertEqual(
            manifest["homepage"],
            "https://github.com/joserey7/codex-orchestrator#readme",
        )
        self.assertEqual(
            manifest["repository"], "https://github.com/joserey7/codex-orchestrator"
        )
        self.assertEqual(manifest["author"]["name"], "codex-orchestrator contributors")
        self.assertEqual(
            manifest["author"]["url"], "https://github.com/joserey7/codex-orchestrator"
        )
        self.assertEqual(manifest["interface"]["displayName"], "codex-orchestrator")
        self.assertEqual(
            manifest["interface"]["developerName"], "codex-orchestrator contributors"
        )
        self.assertTrue(
            any(
                "$codex-orchestrator:orchestration" in prompt
                for prompt in manifest["interface"]["defaultPrompt"]
            )
        )

        for example in sorted((PACKAGE / "examples").glob("*.json")):
            text = example.read_text(encoding="utf-8").lower()
            self.assertNotIn("astra-advisor", text, example.name)
            self.assertNotIn("plugins/astra-advisor", text, example.name)
            self.assertNotIn("$astra-advisor:", text, example.name)

    def test_policy_and_skill_contract_anchors_are_present(self) -> None:
        skill = (PACKAGE / "skills" / "orchestration" / "SKILL.md").read_text(
            encoding="utf-8"
        )
        for anchor in (
            "CODEX ORCHESTRATOR ROUTE",
            "CODEX ORCHESTRATOR REVIEW",
            "API-EQUIVALENT COST RECEIPT",
            "references/routing-policy.md",
            "references/operations.md",
        ):
            self.assertIn(anchor, skill)

        policy_path = PACKAGE / "skills" / "orchestration" / "references" / "routing-policy.md"
        # These anchors catch accidental contract removal; prose review is still required
        # because tests cannot establish semantic policy compliance.
        policy = " ".join(policy_path.read_text(encoding="utf-8").lower().split())
        for anchor in (
            "final acceptance authority",
            "capacity is not justification for delegation",
            "no external skills are required",
            "## bounded delegation contract",
            "maximum live-supported effort",
            "the parent always makes final acceptance",
        ):
            self.assertIn(anchor, policy)

        operations = (
            PACKAGE / "skills" / "orchestration" / "references" / "operations.md"
        ).read_text(encoding="utf-8")
        for anchor in (
            "API-EQUIVALENT COST RECEIPT",
            "cost_receipt.py",
            "whole_task",
            "delegated_only",
        ):
            self.assertIn(anchor, operations)

    def test_invalid_manifest_link_and_license_notice_are_reported(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            copied = self.copy_repo(Path(directory))
            manifest_path = copied / "plugins" / "codex-orchestrator" / ".codex-plugin" / "plugin.json"
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            manifest["name"] = "wrong-name"
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
            self.assertTrue(
                any("plugin manifest.name" in error for error in self.validation_errors(copied))
            )

            manifest["name"] = "codex-orchestrator"
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
            readme_path = copied / "README.md"
            readme_path.write_text(
                readme_path.read_text(encoding="utf-8") + "\n[broken](missing-target.md)\n",
                encoding="utf-8",
            )
            self.assertTrue(
                any("missing-target.md" in error and "missing file" in error for error in self.validation_errors(copied))
            )

            readme_path.write_text(
                readme_path.read_text(encoding="utf-8").replace(
                    "\n[broken](missing-target.md)\n", ""
                ),
                encoding="utf-8",
            )
            license_path = copied / "LICENSE"
            original_license = license_path.read_text(encoding="utf-8")
            license_path.write_text(
                original_license.replace(
                    "Copyright (c) 2026 Daniel McAteer", "Copyright (c) 2026 Someone Else"
                ),
                encoding="utf-8",
            )
            self.assertTrue(
                any("existing MIT attribution" in error for error in self.validation_errors(copied))
            )

            license_path.write_text(original_license, encoding="utf-8")
            package_license = copied / "plugins" / "codex-orchestrator" / "LICENSE"
            package_license.write_text(
                original_license.replace("MIT License", "MIT License (modified)"),
                encoding="utf-8",
            )
            self.assertTrue(
                any("package LICENSE must match root LICENSE" in error for error in self.validation_errors(copied))
            )

    def test_verifier_runs_isolated_without_external_dependencies(self) -> None:
        completed = subprocess.run(
            [sys.executable, "-I", str(VERIFY), "--repo", str(REPO), "--skip-tests"],
            cwd=Path(tempfile.gettempdir()),
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertIn("VERIFY PASSED", completed.stdout)

    def test_calculator_works_from_arbitrary_cwd_and_paths_with_spaces(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            cwd = Path(directory) / "arbitrary cwd with spaces"
            package = cwd / "package path with spaces"
            cwd.mkdir()
            shutil.copytree(PACKAGE, package)
            completed = subprocess.run(
                [
                    sys.executable,
                    str(package / "scripts" / "cost_receipt.py"),
                    str(package / "examples" / "illustrative-usage.json"),
                ],
                cwd=cwd,
                check=False,
                capture_output=True,
                text=True,
            )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertTrue(json.loads(completed.stdout)["illustrative"])


if __name__ == "__main__":
    unittest.main()
