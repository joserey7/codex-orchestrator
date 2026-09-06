#!/usr/bin/env python3
"""Validate the codex-orchestrator package and its repository contract."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import unquote, urlsplit


PLUGIN_NAME = "codex-orchestrator"
PLUGIN_VERSION = "0.3.0"
REPOSITORY_URL = "https://github.com/joserey7/codex-orchestrator"
AUTHOR_NAME = "codex-orchestrator contributors"
LICENSE_ATTRIBUTION = "Copyright (c) 2026 Daniel McAteer"
UPSTREAM_URL = "https://github.com/DannyMac180/astra-advisor"
LEGACY_NAME = "astra-advisor"
HISTORICAL_FILES = {"README.md", "CONTRIBUTING.md", "CHANGELOG.md", "LICENSE"}
TEXT_SUFFIXES = {".json", ".md", ".sh", ".yaml", ".yml", ".txt"}


def _default_repo() -> Path:
    """Return the repository containing this package, independent of cwd."""

    package = Path(__file__).resolve().parents[1]
    return package.parent.parent


def _reject_nonfinite(raw: str) -> None:
    raise ValueError(f"non-finite JSON number is invalid: {raw}")


def markdown_links(text: str) -> list[str]:
    """Return Markdown link destinations while leaving prose unrestricted."""

    return re.findall(r"\[[^\]]+\]\(([^)\s]+)(?:\s+[^)]*)?\)", text)


def _require(condition: bool, errors: list[str], message: str) -> None:
    if not condition:
        errors.append(message)


def _load_json(path: Path, label: str, errors: list[str]):
    _require(path.is_file(), errors, f"missing {label}: {path}")
    if not path.is_file():
        return None
    try:
        return json.loads(
            path.read_text(encoding="utf-8"), parse_constant=_reject_nonfinite
        )
    except (OSError, UnicodeError, ValueError, json.JSONDecodeError) as exc:
        errors.append(f"invalid JSON in {label}: {exc}")
        return None


def _mapping(value, label: str, errors: list[str]) -> dict:
    _require(isinstance(value, dict), errors, f"{label} must be a JSON object")
    return value if isinstance(value, dict) else {}


def _string(mapping: dict, key: str, label: str, errors: list[str], expected=None) -> None:
    value = mapping.get(key)
    _require(
        isinstance(value, str) and bool(value.strip()),
        errors,
        f"{label}.{key} must be a non-empty string",
    )
    if expected is not None:
        _require(value == expected, errors, f"{label}.{key} must equal {expected!r}")


def _string_list(value, label: str, errors: list[str]) -> None:
    _require(isinstance(value, list), errors, f"{label} must be an array")
    if isinstance(value, list):
        _require(
            all(isinstance(item, str) and bool(item.strip()) for item in value),
            errors,
            f"{label} must contain only non-empty strings",
        )


def _check_markdown_links(repo: Path, errors: list[str]) -> None:
    root = repo.resolve()
    for path in sorted(repo.rglob("*.md")):
        if ".git" in path.parts:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as exc:
            errors.append(f"cannot read Markdown file {path}: {exc}")
            continue
        label = f"{path.relative_to(repo)} link"
        for raw_target in markdown_links(text):
            parsed = urlsplit(raw_target)
            if parsed.scheme or parsed.netloc or raw_target.startswith("#"):
                continue
            if not parsed.path:
                continue
            target = (path.parent / unquote(parsed.path)).resolve()
            _require(
                target.is_relative_to(root),
                errors,
                f"{label} escapes the repository: {raw_target}",
            )
            _require(
                target.is_file(),
                errors,
                f"{label} points to a missing file: {raw_target}",
            )


def _check_stale_identity(repo: Path, plugin: Path, errors: list[str]) -> None:
    legacy_path_markers = (
        "$astra-advisor",
        "astra-advisor@",
        "plugins/astra-advisor",
        "/astra-advisor",
    )
    for path in sorted(repo.rglob("*")):
        if not path.is_file() or ".git" in path.parts or path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        if plugin / "tests" in path.parents:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as exc:
            errors.append(f"cannot inspect identity in {path}: {exc}")
            continue
        lowered = text.lower()
        if LEGACY_NAME not in lowered and "astra advisor" not in lowered:
            continue
        relative = path.relative_to(repo)
        if path.name in HISTORICAL_FILES:
            # Historical attribution may name the upstream project. CONTRIBUTING also
            # documents the one-time directory migration; neither grants old runtime
            # invocations or operational paths permission to remain.
            attribution_only = lowered.replace(UPSTREAM_URL.lower(), "").replace(
                "dannymac180/astra-advisor", ""
            )
            if path.name == "CONTRIBUTING.md" and "the only directory move" in lowered:
                attribution_only = attribution_only.replace("plugins/astra-advisor", "")
            for marker in legacy_path_markers:
                if marker in attribution_only:
                    errors.append(
                        f"stale {LEGACY_NAME} invocation or path in historical file {relative}"
                    )
            continue
        errors.append(f"stale {LEGACY_NAME} identity reference: {relative}")


def _check_skill_contract(plugin: Path, errors: list[str]) -> None:
    skill_root = plugin / "skills" / "orchestration"
    skill_path = skill_root / "SKILL.md"
    operations_path = skill_root / "references" / "operations.md"
    policy_path = skill_root / "references" / "routing-policy.md"
    ui_path = skill_root / "agents" / "openai.yaml"
    for path, label in (
        (skill_path, "orchestration skill"),
        (operations_path, "operations reference"),
        (policy_path, "routing policy"),
        (ui_path, "orchestration UI metadata"),
    ):
        _require(path.is_file(), errors, f"missing {label}: {path}")

    if skill_path.is_file():
        skill_text = skill_path.read_text(encoding="utf-8")
        _require(skill_text.startswith("---\n"), errors, "orchestration skill must start with frontmatter")
        frontmatter_end = skill_text.find("\n---", 4)
        _require(frontmatter_end != -1, errors, "orchestration skill frontmatter must close")
        if frontmatter_end != -1:
            frontmatter = skill_text[4:frontmatter_end]
            frontmatter_lines = {}
            for line in frontmatter.splitlines():
                key, separator, value = line.partition(":")
                if separator:
                    frontmatter_lines[key.strip()] = value.strip().strip('"').strip("'")
            _require(
                frontmatter_lines.get("name") == "orchestration",
                errors,
                "orchestration skill frontmatter.name must be orchestration",
            )
            _require(
                bool(frontmatter_lines.get("description")),
                errors,
                "orchestration skill frontmatter.description must be non-empty",
            )
        normalized_skill = " ".join(skill_text.split()).lower()
        for anchor in (
            "CODEX ORCHESTRATOR ROUTE",
            "CODEX ORCHESTRATOR REVIEW",
            "API-EQUIVALENT COST RECEIPT",
            "references/routing-policy.md",
            "references/operations.md",
        ):
            _require(
                anchor.lower() in normalized_skill,
                errors,
                f"orchestration skill missing contract anchor: {anchor}",
            )

    if policy_path.is_file():
        policy = " ".join(policy_path.read_text(encoding="utf-8").lower().split())
        for anchor in (
            "final acceptance authority",
            "capacity is not justification for delegation",
            "no external skills are required",
            "## bounded delegation contract",
            "maximum live-supported effort",
            "the parent always makes final acceptance",
        ):
            _require(anchor in policy, errors, f"routing policy missing contract anchor: {anchor}")

    if operations_path.is_file():
        operations = operations_path.read_text(encoding="utf-8")
        for anchor in (
            "API-EQUIVALENT COST RECEIPT",
            "cost_receipt.py",
            "whole_task",
            "delegated_only",
        ):
            _require(anchor in operations, errors, f"operations reference missing contract anchor: {anchor}")


def _check_manifest(repo: Path, plugin: Path, errors: list[str]) -> None:
    manifest_path = plugin / ".codex-plugin" / "plugin.json"
    manifest = _mapping(_load_json(manifest_path, "plugin manifest", errors), "plugin manifest", errors)
    _string(manifest, "name", "plugin manifest", errors, PLUGIN_NAME)
    _string(manifest, "version", "plugin manifest", errors, PLUGIN_VERSION)
    _string(manifest, "description", "plugin manifest", errors)
    _string(manifest, "homepage", "plugin manifest", errors, f"{REPOSITORY_URL}#readme")
    _string(manifest, "repository", "plugin manifest", errors, REPOSITORY_URL)
    _string(manifest, "license", "plugin manifest", errors, "MIT")
    _require(manifest.get("skills") == "./skills/", errors, "plugin manifest.skills must be ./skills/")

    keywords = manifest.get("keywords")
    _string_list(keywords, "plugin manifest.keywords", errors)
    if isinstance(keywords, list):
        _require("orchestration" in keywords, errors, "plugin manifest.keywords must include orchestration")

    author = _mapping(manifest.get("author"), "plugin manifest.author", errors)
    _string(author, "name", "plugin manifest.author", errors, AUTHOR_NAME)
    _string(author, "url", "plugin manifest.author", errors, REPOSITORY_URL)

    interface = _mapping(manifest.get("interface"), "plugin manifest.interface", errors)
    for key, expected in (
        ("displayName", PLUGIN_NAME),
        ("developerName", AUTHOR_NAME),
        ("category", "Productivity"),
        ("websiteURL", REPOSITORY_URL),
    ):
        _string(interface, key, "plugin manifest.interface", errors, expected)
    for key in ("shortDescription", "longDescription"):
        _string(interface, key, "plugin manifest.interface", errors)
    capabilities = interface.get("capabilities")
    _string_list(capabilities, "plugin manifest.interface.capabilities", errors)
    if isinstance(capabilities, list):
        _require(
            {"Interactive", "Write"}.issubset(capabilities),
            errors,
            "plugin manifest.interface.capabilities must include Interactive and Write",
        )
    default_prompt = interface.get("defaultPrompt")
    _string_list(default_prompt, "plugin manifest.interface.defaultPrompt", errors)
    if isinstance(default_prompt, list):
        _require(
            any("$codex-orchestrator:orchestration" in item for item in default_prompt),
            errors,
            "defaultPrompt must invoke $codex-orchestrator:orchestration",
        )


def _check_marketplace(repo: Path, errors: list[str]) -> None:
    marketplace_path = repo / ".agents" / "plugins" / "marketplace.json"
    marketplace = _mapping(_load_json(marketplace_path, "marketplace", errors), "marketplace", errors)
    _string(marketplace, "name", "marketplace", errors, PLUGIN_NAME)
    interface = _mapping(marketplace.get("interface"), "marketplace.interface", errors)
    _string(interface, "displayName", "marketplace.interface", errors, PLUGIN_NAME)
    entries = marketplace.get("plugins")
    _require(isinstance(entries, list), errors, "marketplace.plugins must be an array")
    matches = [entry for entry in entries if isinstance(entry, dict) and entry.get("name") == PLUGIN_NAME] if isinstance(entries, list) else []
    _require(len(matches) == 1, errors, f"marketplace must contain exactly one {PLUGIN_NAME} entry")
    if len(matches) == 1:
        entry = matches[0]
        source = _mapping(entry.get("source"), "marketplace entry.source", errors)
        _string(source, "source", "marketplace entry.source", errors, "local")
        _string(source, "path", "marketplace entry.source", errors, f"./plugins/{PLUGIN_NAME}")
        policy = _mapping(entry.get("policy"), "marketplace entry.policy", errors)
        _string(policy, "installation", "marketplace entry.policy", errors, "AVAILABLE")
        _string(policy, "authentication", "marketplace entry.policy", errors, "ON_INSTALL")
        _string(entry, "category", "marketplace entry", errors, "Productivity")
        source_target = repo / "plugins" / PLUGIN_NAME
        _require(
            (source_target / ".codex-plugin" / "plugin.json").is_file(),
            errors,
            "marketplace source path must resolve to the plugin manifest",
        )


def _check_repository_files(repo: Path, plugin: Path, errors: list[str]) -> None:
    pricing_path = plugin / "pricing" / "2026-09-04.json"
    examples_path = plugin / "examples"
    _require(pricing_path.is_file(), errors, f"missing pricing snapshot: {pricing_path}")
    _require(examples_path.is_dir(), errors, f"missing examples directory: {examples_path}")
    for relative, label in (
        (Path("scripts") / "cost_receipt.py", "cost receipt calculator"),
        (Path("scripts") / "verify.py", "portable verifier"),
        (Path("scripts") / "verify.sh", "shell verifier wrapper"),
        (Path("tests") / "test_cost_receipt.py", "cost receipt tests"),
        (Path("tests") / "test_package.py", "package tests"),
    ):
        _require((plugin / relative).is_file(), errors, f"missing {label}: {plugin / relative}")
    if examples_path.is_dir():
        examples = sorted(examples_path.glob("*.json"))
        _require(bool(examples), errors, "examples directory must contain at least one JSON example")
        for example in examples:
            _load_json(example, f"example {example.relative_to(repo)}", errors)

    license_path = repo / "LICENSE"
    _require(license_path.is_file(), errors, f"missing LICENSE: {license_path}")
    if license_path.is_file():
        license_text = license_path.read_text(encoding="utf-8")
        _require(license_text.startswith("MIT License\n"), errors, "LICENSE must use the MIT license")
        _require(LICENSE_ATTRIBUTION in license_text, errors, "LICENSE must retain the existing MIT attribution")
        package_license = plugin / "LICENSE"
        _require(package_license.is_file(), errors, f"missing package LICENSE: {package_license}")
        if package_license.is_file():
            try:
                package_license_text = package_license.read_text(encoding="utf-8")
            except (OSError, UnicodeError) as exc:
                errors.append(f"cannot read package LICENSE: {exc}")
            else:
                _require(
                    package_license_text == license_text,
                    errors,
                    "package LICENSE must match root LICENSE",
                )

    for filename in ("README.md", "CONTRIBUTING.md", "CHANGELOG.md"):
        _require((repo / filename).is_file(), errors, f"missing repository document: {repo / filename}")

    gitignore_path = repo / ".gitignore"
    _require(gitignore_path.is_file(), errors, f"missing .gitignore: {gitignore_path}")
    if gitignore_path.is_file():
        ignored = {
            line.strip()
            for line in gitignore_path.read_text(encoding="utf-8").splitlines()
            if line.strip() and not line.lstrip().startswith("#")
        }
        _require("*.log" in ignored and "logs/" in ignored, errors, ".gitignore must exclude log files and the logs directory")

    workflow_path = repo / ".github" / "workflows" / "verify.yml"
    _require(workflow_path.is_file(), errors, f"missing CI workflow: {workflow_path}")
    if workflow_path.is_file():
        workflow = workflow_path.read_text(encoding="utf-8")
        for anchor in (
            "actions/checkout@v4",
            "actions/setup-python@v5",
            f"plugins/{PLUGIN_NAME}/scripts/verify.py",
            "ubuntu-latest",
            "windows-latest",
            "macos-latest",
            "3.11",
            "3.12",
        ):
            _require(anchor in workflow, errors, f"CI workflow missing portability anchor: {anchor}")

    for path in plugin.rglob("*"):
        if path.is_file() and path.suffix == ".toml":
            errors.append(f"static role TOML is not allowed: {path.relative_to(plugin)}")
    _require(
        not (plugin / "scripts" / "install-agents.sh").exists(),
        errors,
        "companion installer is not allowed",
    )


def validate_package(repo: Path | str | None = None) -> list[str]:
    """Return all package validation errors without running tests or printing output."""

    root = Path(repo) if repo is not None else _default_repo()
    root = root.expanduser().resolve()
    errors: list[str] = []
    plugin = root / "plugins" / PLUGIN_NAME
    _require(plugin.is_dir(), errors, f"missing plugin directory: {plugin}")
    _check_manifest(root, plugin, errors)
    _check_skill_contract(plugin, errors)
    _check_marketplace(root, errors)
    _check_repository_files(root, plugin, errors)
    _check_markdown_links(root, errors)
    _check_stale_identity(root, plugin, errors)
    return errors


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--repo",
        type=Path,
        default=None,
        help="repository root (defaults to the repository containing this script)",
    )
    parser.add_argument(
        "--skip-tests",
        action="store_true",
        help="skip the unittest subprocess; intended for verifier self-tests",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    repo = (args.repo or _default_repo()).expanduser().resolve()
    errors = validate_package(repo)
    if not args.skip_tests:
        plugin = repo / "plugins" / PLUGIN_NAME
        tests = plugin / "tests"
        if not tests.is_dir():
            errors.append(f"missing package tests: {tests}")
        else:
            result = subprocess.run(
                [sys.executable, "-B", "-m", "unittest", "discover", "-s", str(tests), "-p", "test_*.py"],
                cwd=repo,
                check=False,
            )
            if result.returncode != 0:
                errors.append("package tests failed")

    if errors:
        print("VERIFY FAILED")
        for error in errors:
            print(f"- {error}")
        return 1
    print("VERIFY PASSED")
    print("manifest, package identity, links, policy anchors, license, CI, and static-role boundaries are valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
