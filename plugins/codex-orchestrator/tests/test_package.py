from __future__ import annotations

import importlib.util
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
PACKAGE = REPO / "plugins" / "codex-orchestrator"
VERIFY = PACKAGE / "scripts" / "verify.py"
SPEC = importlib.util.spec_from_file_location("verify", VERIFY)
assert SPEC and SPEC.loader
verify = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(verify)


class PackageTests(unittest.TestCase):
    def test_repository_contract(self):
        self.assertEqual(verify.validate_package(REPO), [])

    def test_manifest_version_and_identity(self):
        manifest = json.loads((PACKAGE / ".codex-plugin" / "plugin.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["version"], "0.4.0")
        self.assertEqual(manifest["name"], "codex-orchestrator")
        self.assertTrue(any("$codex-orchestrator:orchestration" in p for p in manifest["interface"]["defaultPrompt"]))

    def test_accounting_is_outside_installed_plugin(self):
        self.assertFalse((PACKAGE / "scripts" / "cost_receipt.py").exists())
        self.assertFalse((PACKAGE / "pricing").exists())
        self.assertTrue((REPO / "tools" / "accounting" / "scripts" / "cost_receipt.py").is_file())
        self.assertTrue((REPO / "tools" / "accounting" / "tests" / "test_cost_receipt.py").is_file())

    def test_license_attribution_is_preserved(self):
        root = (REPO / "LICENSE").read_text(encoding="utf-8")
        self.assertIn("Copyright (c) 2026 Daniel McAteer", root)
        self.assertEqual(root, (PACKAGE / "LICENSE").read_text(encoding="utf-8"))

    def test_verifier_is_portable_from_arbitrary_cwd(self):
        with tempfile.TemporaryDirectory() as directory:
            completed = subprocess.run([sys.executable, "-I", str(VERIFY), "--repo", str(REPO), "--skip-tests"],
                                       cwd=directory, check=False, capture_output=True, text=True)
        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
        self.assertIn("VERIFY PASSED", completed.stdout)

    def test_broken_link_is_reported(self):
        with tempfile.TemporaryDirectory() as directory:
            copied = Path(directory) / "repo with spaces"
            shutil.copytree(REPO, copied, ignore=shutil.ignore_patterns(".git", "__pycache__"))
            readme = copied / "README.md"
            readme.write_text(readme.read_text(encoding="utf-8") + "\n[broken](missing.md)\n", encoding="utf-8")
            self.assertTrue(any("missing.md" in e for e in verify.validate_package(copied)))


if __name__ == "__main__":
    unittest.main()
