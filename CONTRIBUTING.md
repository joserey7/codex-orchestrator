# Contributing to codex-orchestrator

Keep this a focused native Codex orchestration plugin. Prefer small inspectable policy/validation changes over a custom scheduler or inference runtime. Explain the concrete behavior, evidence and negative cases.

## Local development

Use Git and Python 3.11+ (3.12 recommended) on Windows, Linux or macOS. No third-party Python dependencies are required.

```text
python plugins/codex-orchestrator/scripts/verify.py
```

CI runs Python 3.12 on all three OSes and Python 3.11 on Ubuntu. Keep shared tooling portable (`pathlib`, `sys.executable`, argument-list subprocesses, no required shell).

## Boundaries

- `SKILL.md`: compact entry policy loaded for orchestration.
- `references/routing-policy.md`: model lanes, states, risk/review, contracts, overrides and budgets.
- `references/operations.md`: live preflight, evidence, lifecycle and acceptance.
- `references/evaluation.md`: optional development benchmarking; not normal task context.
- `scripts/routing_policy.py`: offline check of a caller-supplied classification; not a natural-language classifier/scheduler.
- `scripts/task_state.py`: advisory validation of declared coordination/evidence; not runtime enforcement.
- `tools/accounting/`: preserved historical upstream accounting, outside the installed plugin and normal verification path.

Tests must cover behavior and negative cases, not merely prose anchors. They cannot prove first-attempt model quality, live model pins or subscription savings. Unknown runtime/usage evidence remains unknown.

Do not add another public mode or default model lane without evidence that the simpler policy cannot express a useful case. Sol remains an explicit user override unless benchmark evidence justifies revisiting that decision. Ultra is not a default Luna effort when it changes agent topology.

Before submitting, run verification, inspect the complete diff, and obtain an appropriate fresh review. Update public docs/changelog for behavior changes.

## Native host smoke check

Offline CI is insufficient for a release. Record the exact client/version and account context in a disposable project and follow `references/evaluation.md`. Confirm economy/balanced routes, wait/skip semantics, risk review, override behavior, missing-control failure, realized-setting mismatch handling and current-revision acceptance. Report smoke evidence separately from CI.

## Optional accounting

Historical API-equivalent accounting lives under `tools/accounting/` only for manual/reference use. It is not a runtime dependency and must not be presented as ChatGPT Pro/Codex quota measurement. Keep historical pricing snapshots immutable.

## Upstream and licensing

The fork foundation is [DannyMac180/astra-advisor](https://github.com/DannyMac180/astra-advisor). Preserve its MIT copyright/permission notice in root and installed-package LICENSE files. Other acknowledged projects are conceptual inspiration unless their licenses are explicitly reviewed before importing source.
