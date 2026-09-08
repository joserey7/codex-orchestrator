# Optional evaluation and host compatibility

This is development guidance, not normal orchestration context. Do not run telemetry/accounting work merely to complete a user task.

## What to evaluate

The project optimizes **correctly accepted work per available subscription capacity**, not delegate count or API-dollar estimates. Raw token counts and API repricing are not direct ChatGPT Pro/Codex quota measurements.

When the host already exposes trustworthy telemetry, record separately:

- client/version, OS and plan,
- exact starting repository/worktree state and prompt,
- configuration: root-only, economy, balanced (and explicit experiments),
- requested and observed model/effort when available,
- uncached input, cached input, output/reasoning tokens when explicitly recorded,
- rate-limit percentages when explicitly recorded, noting they are account-wide,
- dispatch/review/correction counts, wall time, verification and acceptance result.

Never infer missing counters from text length, treat unknown as zero, or claim a percentage saving from a single run.

## Benchmark protocol

Use 3-4 representative tasks: localized fix, multi-file feature, cross-component bug, research-heavy change. Reuse prompts and starting state. Compare at least root-only Astra, economy and balanced; explicit Sol or other overrides are experiments, not default lanes. Repeat each cell multiple times because model/runtime variance is real.

Compare correctness/acceptance first, then subscription-window deltas when observable, then wall time and token categories. Other simultaneous Codex activity contaminates account-wide rate-limit deltas; disclose it.

## Release smoke check

Offline tests cannot prove plugin installation or realized model pins. For a release, record the exact host/client version and test in a disposable project:

1. install the checkout and start a fresh Astra task,
2. confirm economy routes mechanical -> Luna Medium and bounded -> Luna maximum individual,
3. confirm balanced routes bounded -> Luna maximum individual and justified judgment -> Terra High,
4. confirm difficult work stays with Astra unless a fresh Astra handoff is explicitly justified,
5. confirm Sol is not selected without a user override,
6. confirm capacity/dependency waits do not become parent execution,
7. confirm exceptional risk requires an Astra decision and current fresh review,
8. confirm missing controls/mismatched observed settings fail closed without substitution,
9. confirm `task_state.py` catches stale review/current-revision and ownership/capacity mistakes.

Publish smoke results separately from CI. A green CI run proves offline contracts only.
