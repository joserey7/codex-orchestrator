# Operations

Read this only when live dispatch/review details are needed. The routing policy is authoritative for model selection.

## Parent and preflight

The primary session must be GPT-6 Astra for an Astra-orchestrated claim. Preserve the user's parent effort; Astra Low is a recommendation, not an automatic change. If parent model/effort is observable, record it. If it is unobservable, say so. Never treat a request value as realized evidence.

Before dispatch, inspect the current native tool schema. Require explicit model, supported effort and fresh-context controls, and record the source. Live schemas outrank this document. Missing/conflicting controls block that route; do not silently substitute models or launch a separate inference mechanism as a workaround.

Use the generic native spawn interface only when exposed. Pass explicit model/effort and fresh context (`fork_turns: none` when that is the current public field). Luna's `maximum individual` is the highest confirmed individual effort and intentionally excludes a setting such as Ultra when it also enables autonomous descendants.

Current intended lanes, subject to live support:

- Economy: Luna Medium mechanical; Luna maximum-individual bounded; Astra parent for judgment/difficult, with documented exceptional Terra / High handoff.
- Balanced: Luna maximum-individual mechanical/bounded; Terra / High judgment; Astra parent difficult.
- Fresh Astra / Low delegate: only when a difficult independent deliverable benefits from separate context/parallelism.
- Sol: explicit user override only.

## Lifecycle and coordination

Keep user-visible progress compact. One plan update plus meaningful changes is enough unless the user asks for detailed orchestration. Do not narrate every poll or spawn.

For each dispatch retain internally/declared-state: task ID, ownership, dependencies, requested model/effort, source of controls, runtime observations when available, result evidence, and disposition. Requested settings remain unconfirmed until observed. On mismatch, stop affected work and reverify. Unobservable settings are disclosed; they block only work whose contract explicitly requires routing proof.

`wait` means wait for capacity/dependencies/serialization; it does not authorize parent execution. `skip` means do not perform the work. Do not exceed economy 2 / balanced 3 active delegates or a lower host limit. Descendants count. Prefer a few complete, verifiable deliverables over micro-delegation.

Partition writers by non-overlapping file/directory scopes. Reviewers are fresh read-only contexts when the host can enforce/observe that; otherwise do not claim technical isolation. A reviewer never fixes its own findings.

## Budget and acceptance

Set a small budget before dispatch for total dispatches, correction cycles and reviews. A limit is a reassessment gate: if exceeded, stop unchanged retry behavior, inspect why, and explicitly revise the plan if continued work is justified. Never use a budget to waive correctness.

Before acceptance, Astra:

1. identifies the complete accumulated diff/revision (including dirty work, not merely HEAD),
2. inspects that diff and relevant evidence,
3. runs/confirms highest-value tests/checks,
4. ensures required work completed or has an explicit completed replacement,
5. ensures the required fresh review inspected that exact revision and returned `ship`,
6. records residual risks/limitations and accepts.

Use `scripts/task_state.py INPUT.json --acceptance` as an optional consistency check. It validates assertions; it does not intercept Codex or independently prove them.

## Host boundaries

Native capabilities vary by client, version and account. Record the client/version during release smoke checks. A package being cross-platform does not imply every host exposes model-pinned subagents. For ChatGPT/Codex Desktop, use only controls exposed by its current native interface. Separate app/cloud tasks require the user's explicit request. Never fabricate equivalent controls.

## Accounting boundary

Accounting is intentionally outside the installed orchestration plugin. Normal tasks do not load pricing/token instructions or emit API-equivalent receipts. Historical upstream accounting is retained under repository-root `tools/accounting/` for manual development/reference only; it does not measure ChatGPT Pro/Codex quota and is not a runtime dependency.

Use [evaluation](evaluation.md) for a small optional measurement protocol based only on telemetry already available. Unknown usage remains unknown, never zero.
