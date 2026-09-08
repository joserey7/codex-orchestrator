#!/usr/bin/env python3
"""Portable repository/package verification for codex-orchestrator."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from urllib.parse import unquote, urlsplit

PLUGIN = "codex-orchestrator"
VERSION = "0.4.0"
REPO_URL = "https://github.com/joserey7/codex-orchestrator"
ATTRIBUTION = "Copyright (c) 2026 Daniel McAteer"


def repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def markdown_links(text: str) -> list[str]:
    import re
    return re.findall(r"\[[^\]]+\]\(([^)\s]+)(?:\s+[^)]*)?\)", text)


def validate_package(repo: Path) -> list[str]:
    errors: list[str] = []
    package = repo / "plugins" / PLUGIN
    manifest_path = package / ".codex-plugin" / "plugin.json"
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"),
                              parse_constant=lambda raw: (_ for _ in ()).throw(ValueError(raw)))
    except (OSError, UnicodeError, ValueError, json.JSONDecodeError) as exc:
        return [f"invalid plugin manifest: {exc}"]
    expected = {"name": PLUGIN, "version": VERSION, "repository": REPO_URL,
                "homepage": REPO_URL + "#readme", "license": "MIT", "skills": "./skills/"}
    for key, value in expected.items():
        if manifest.get(key) != value:
            errors.append(f"plugin manifest.{key} must equal {value!r}")
    interface = manifest.get("interface") if isinstance(manifest.get("interface"), dict) else {}
    if interface.get("displayName") != PLUGIN:
        errors.append("plugin manifest.interface.displayName must equal codex-orchestrator")
    if not {"Interactive", "Write"}.issubset(set(interface.get("capabilities") or [])):
        errors.append("plugin capabilities must include Interactive and Write")
    prompts = interface.get("defaultPrompt") or []
    if not any("$codex-orchestrator:orchestration" in p for p in prompts if isinstance(p, str)):
        errors.append("default prompt must invoke orchestration skill")
    marketplace_path = repo / ".agents" / "plugins" / "marketplace.json"
    try:
        marketplace = json.loads(marketplace_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, ValueError, json.JSONDecodeError) as exc:
        errors.append(f"invalid marketplace: {exc}")
        marketplace = {}
    entries = marketplace.get("plugins") if isinstance(marketplace, dict) else None
    if not isinstance(entries, list) or len([e for e in entries if isinstance(e, dict) and e.get("name") == PLUGIN]) != 1:
        errors.append("marketplace must contain exactly one codex-orchestrator entry")
    required = [
        package / "LICENSE", package / "scripts" / "routing_policy.py", package / "scripts" / "task_state.py",
        package / "skills" / "orchestration" / "SKILL.md",
        package / "skills" / "orchestration" / "references" / "routing-policy.md",
        package / "skills" / "orchestration" / "references" / "operations.md",
        package / "skills" / "orchestration" / "references" / "evaluation.md",
        package / "examples" / "routing-cases.json", package / "examples" / "task-state.json",
        repo / "tools" / "accounting" / "scripts" / "cost_receipt.py",
        repo / "tools" / "accounting" / "tests" / "test_cost_receipt.py",
        repo / "tools" / "accounting" / "pricing" / "2026-09-04.json",
    ]
    for path in required:
        if not path.is_file():
            errors.append(f"missing required file: {path.relative_to(repo)}")
    for forbidden in (package / "scripts" / "cost_receipt.py", package / "pricing" / "2026-09-04.json"):
        if forbidden.exists():
            errors.append(f"accounting must not ship in installed plugin: {forbidden.relative_to(repo)}")
    try:
        root_license = (repo / "LICENSE").read_text(encoding="utf-8")
        package_license = (package / "LICENSE").read_text(encoding="utf-8")
        if ATTRIBUTION not in root_license:
            errors.append("root LICENSE must retain upstream MIT attribution")
        if root_license != package_license:
            errors.append("installed package LICENSE must match root LICENSE")
    except (OSError, UnicodeError) as exc:
        errors.append(f"cannot read licenses: {exc}")
    root = repo.resolve()
    for path in repo.rglob("*.md"):
        if ".git" in path.parts:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as exc:
            errors.append(f"cannot read {path}: {exc}")
            continue
        for target in markdown_links(text):
            parsed = urlsplit(target)
            if parsed.scheme or parsed.netloc or target.startswith("#") or not parsed.path:
                continue
            resolved = (path.parent / unquote(parsed.path)).resolve()
            if not resolved.is_relative_to(root) or not resolved.is_file():
                errors.append(f"broken/escaping Markdown link in {path.relative_to(repo)}: {target}")
    skill = (package / "skills" / "orchestration" / "SKILL.md")
    if skill.is_file():
        text = skill.read_text(encoding="utf-8")
        for anchor in ("Astra Low", "Luna / Medium", "Terra / High", "Sol is not a default lane",
                       "`wait`", "scripts/task_state.py", "Cost/accounting is not part"):
            if anchor not in text:
                errors.append(f"skill missing policy anchor: {anchor}")
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=repo_root())
    parser.add_argument("--skip-tests", action="store_true")
    args = parser.parse_args(argv)
    repo = args.repo.resolve()
    errors = validate_package(repo)
    if errors:
        print("VERIFY FAILED")
        for error in errors:
            print("-", error)
        return 2
    if not args.skip_tests:
        suites = [repo / "plugins" / PLUGIN / "tests", repo / "tools" / "accounting" / "tests"]
        for suite in suites:
            completed = subprocess.run([sys.executable, "-m", "unittest", "discover", "-s", str(suite), "-p", "test_*.py"],
                                       cwd=repo, check=False)
            if completed.returncode:
                return completed.returncode
    print("VERIFY PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
