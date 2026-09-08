# codex-orchestrator

**GPT-6 Astra owns architecture and acceptance. Economy emphasizes Astra + Luna; balanced adds Terra for bounded engineering judgment.**

codex-orchestrator is a public MIT-licensed Codex plugin evolved from Astra Advisor. Its rule is to select the cheapest model highly likely to complete a useful bounded deliverable correctly on the first attempt. It optimizes correctly accepted work rather than delegate count, API-dollar estimates, or a claimed subscription-saving percentage.

## Install

```text
codex plugin marketplace add joserey7/codex-orchestrator --ref main
codex plugin add codex-orchestrator@codex-orchestrator
```

For an unreleased checkout, run the same marketplace command with `.` from the repository root. Start a fresh task after installing/upgrading. Select **GPT-6 Astra** as the parent; the skill cannot change the parent model/effort. **Astra Low is the recommended starting point**, but the user's selected effort remains authoritative.

Invoke:

```text
Use $codex-orchestrator:orchestration in balanced mode to implement this feature.
Use $codex-orchestrator:orchestration in economy mode to fix this bounded bug.
```

Python 3.11+ is required for repository verification/offline policy helpers; 3.12 is recommended. Core orchestration uses native host tools. The package targets Windows, Linux and macOS, but actual model-pinned subagent support depends on client/version/account capabilities.

## Modes

| Work | Economy | Balanced |
| --- | --- | --- |
| Mechanical/read-only/routine commands | `gpt-5.6-luna` / Medium | `gpt-5.6-luna` / maximum individual reasoning |
| Explicit bounded implementation/debugging | Luna / maximum individual | Luna / maximum individual |
| Meaningful local engineering judgment | Astra resolves/decomposes; exceptional Terra handoff only when justified | `gpt-5.6-terra` / High with a concrete reason |
| Difficult/architecture/important ambiguity | Astra parent | Astra parent |
| Fresh normal-risk review | Astra / Low | Terra / High |
| Fresh high-risk review | Astra / Low | Astra / Low |

Economy allows at most 2 active delegates; balanced 3, or a lower host limit. These are limits, not targets.

`maximum individual reasoning` means the highest confirmed effort that is purely individual reasoning. Do not automatically treat Ultra as a bigger Max if the runtime also uses it for autonomous subagent delegation; topology changes require a separate explicit user decision.

**Sol is no longer a default lane.** It remains available only as an explicit user override with model, supported effort and reason, so it can be benchmarked without complicating normal routing.

A difficult independent deliverable may use a fresh Astra / Low delegate only when Astra explicitly decides separate context or parallelism is worth the handoff. Otherwise Astra keeps the work. The plugin never builds a Luna -> Terra -> Astra failure ladder.

## Coordination and acceptance

Routing has five distinct states:

- `delegate`: dispatch selected bounded work,
- `parent`: Astra genuinely owns it,
- `wait`: dependencies/capacity/serialization block a later delegation,
- `skip`: redundant/non-useful work is not performed,
- `blocked`: a required control/evidence/authorization is missing.

Full capacity never silently moves work to Astra. Delegability and parallel safety are separate; a serial task can remain a later Luna task. Partition parallel writers by file/directory scope and keep returned evidence concise.

Risk is separate from implementation difficulty. Exceptional security/integrity/concurrency/destructive-migration risk requires an explicit Astra decision even for a mechanical edit. Fresh review is selected by mode/risk; reviewers are read-only fresh contexts and review the complete current accumulated diff. Any correction invalidates the previous verdict.

For non-trivial or consequential work, `scripts/task_state.py` can validate a compact declared task state: dependencies, ownership, capacity, pre-dispatch budgets, requested/observed-setting consistency, current revision, review freshness and acceptance evidence. It is advisory consistency checking, **not** a scheduler, runtime interceptor or proof that a model/sandbox actually ran as declared.

Pre-dispatch budgets cover dispatches, correction cycles and reviews. Exceeding a budget triggers reassessment and explicit replanning; it never permits incomplete acceptance.

See [routing policy](plugins/codex-orchestrator/skills/orchestration/references/routing-policy.md), [operations](plugins/codex-orchestrator/skills/orchestration/references/operations.md) and optional [evaluation guidance](plugins/codex-orchestrator/skills/orchestration/references/evaluation.md).

## Runtime honesty

Live public tool schemas and runtime metadata outrank static documentation. Delegation requires explicit model, effort and fresh-context controls plus a recorded evidence source. Requested settings are not proof of realized settings. Mismatches stop affected work. Unobservable realized settings remain unconfirmed; they block acceptance only when the task explicitly requires routing proof.

Installed compatible engineering skills may guide HOW work is done. `addyosmani/agent-skills` is optional; nothing is auto-installed or required. codex-orchestrator owns WHAT/WHO/model/ownership/coordination/acceptance.

## Accounting and evaluation

API-equivalent accounting is no longer part of the installed plugin or normal task context. The preserved historical upstream calculator/pricing fixture lives under `tools/accounting/` for manual development/reference only. It does **not** measure ChatGPT Pro/Codex quota.

If trustworthy telemetry is already available, the optional evaluation guide describes repeatable root-only vs economy vs balanced comparisons. Unknown usage remains unknown, never zero. Release smoke checks must record client/version separately from automated CI.

## Development

```text
python plugins/codex-orchestrator/scripts/verify.py
```

CI runs Python 3.11/3.12 on Ubuntu and 3.12 on Windows/macOS. Tests cover routing states/model lanes, overrides, risk/review behavior, task-state consistency, package identity/links and historical accounting in its separate repository-root tool area. Offline tests cannot prove natural-language classification quality, live model pins or subscription savings.

## Acknowledgements and license

- [DannyMac180/astra-advisor](https://github.com/DannyMac180/astra-advisor) is the primary upstream/fork foundation: Astra authority, native delegation/evidence safeguards and the preserved historical accounting utility.
- [DannyMac180/sol-advisor](https://github.com/DannyMac180/sol-advisor) inspired bounded capability delegation, selective review and parent acceptance.
- [donvito/codex-astra-luna-orchestrator](https://github.com/donvito/codex-astra-luna-orchestrator) inspired the simplified Astra + Luna economy topology, concise returned context and keeping routine execution away from the root.
- [addyosmani/agent-skills](https://github.com/addyosmani/agent-skills) inspired optional structured engineering workflows.

These relationships do not imply endorsement. This fork retains upstream MIT code and Daniel McAteer's copyright/permission notice in root and installed-package `LICENSE` files. Other projects are conceptual inspiration; do not copy their source without reviewing their licenses.
