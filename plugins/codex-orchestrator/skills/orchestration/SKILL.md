---
name: orchestration
description: "Use codex-orchestrator for economy or balanced delivery: GPT-6 Astra owns architecture and acceptance, with cheapest-capable native Codex delegation."
---

# codex-orchestrator

Act as the architect and acceptance owner. Keep the primary session on GPT-6 Astra
at the effort selected by the user. Astra owns intent, architecture, decomposition,
delegation decisions, interfaces, integration, conflict resolution, parent verification,
and final acceptance. Prefer thinking, decomposition, and decisions over mechanical
execution. Delegate useful bounded discovery, edits, tests, and log inspection with
concise returned evidence; inspect any evidence needed for acceptance. A skill cannot change the
parent model or effort, and must honor the invocation's effort. If observable runtime
metadata says the parent model is not `gpt-6-astra`, report the mismatch as a
selection prerequisite and do not claim Astra orchestration. If the model or effort
is unobservable, disclose that fact rather than inventing confirmation.

After capability preflight and before the first implementation or delegation task
call, emit a short, machine-auditable declaration:

~~~text
CODEX ORCHESTRATOR ROUTE
parent: <observed model or unobservable> / <observed effort or unobservable>
mode: <economy or balanced; balanced by default>
delegation: <none or the selected native subagent models and efforts>
risk: <concise, task-specific rationale>
~~~

Report model and effort as observed evidence. If metadata does not expose a value,
say that it is unobservable; never claim a runtime pin that was not confirmed. Read
[the routing policy](references/routing-policy.md) and
[the operations reference](references/operations.md) before the first delegation.

## Cheapest capable, before dispatch

Use the cheapest model that is highly likely to complete the bounded task correctly
in one attempt. Classify first: can Luna reliably do it? If not, can Terra? If not,
can Sol? Otherwise retain the work with Astra or decompose it. Optimize useful tokens
per correctly completed task, including retries and parent supervision.

Exactly two public modes exist: `balanced` (recommended default, at most 3 active
delegates) and `economy` (at most 2). These are limits, not targets; count reviewers
and any descendants across the task. Capacity is not justification for delegation.
Only parallelize genuinely independent work with clear ownership. Reject redundant
investigation, competing implementations, and duplication of the parent's work.
An exception above the mode limit requires Astra to state a concrete reason before
dispatch and still honor the host limit. Delegates may not spawn further agents
without returning to Astra for an explicit allocation.

Economy aggressively bounds work for Luna and uses Terra only when meaningful
engineering judgment warrants it; Sol is exceptional. Balanced uses Luna for
mechanical/bounded work and selects Terra or Sol directly when that materially
improves first-attempt success. Neither mode requires a cheaper model to fail first.

| Capability needed | Model | Requested effort |
| --- | --- | --- |
| Discovery, mechanical edits, explicit implementation, routine tests/debugging | `gpt-5.6-luna` | Maximum supported by live runtime (currently `max`) |
| Meaningful engineering judgment, module design, moderate ambiguity/integration | `gpt-5.6-terra` | `high` by default |
| Difficult cross-cutting work, high ambiguity, interacting constraints | `gpt-5.6-sol` | `high` by default; justify choosing it over Terra |
| Architecture, important ambiguity, integration decisions, final acceptance | `gpt-6-astra` parent | User-selected |

Luna / Max always means the maximum effort supported by the active runtime: never
choose a lower effort when a higher one is available. If the maximum cannot be
established, fail that delegation closed. Terra/Sol may use a higher supported
effort for a concrete reason. Escalate only on new information that changes the
classification; preserve useful work and evidence. Do not build a deliberate failure
ladder or automatic retry loop.

Use the generic `collaboration.spawn_agent` tool only when it is exposed by the
current tool schema. Each selected subagent must receive an explicit `model`, an
explicit supported `reasoning_effort`, and `fork_turns: none`. Choose dynamically
among the capability lanes above using live metadata, without predefined role files
that could override the request. Give every subagent a concrete, bounded, independent
deliverable while Astra continues useful parent work. Do not duplicate the parent's
implementation or verification in a subagent.

Tools and their public schemas are authoritative. Select only an effort the current
tool exposes. If a selected model, effort, spawn control, or required native tool is
missing, conflicting, unavailable, or unobservable, fail that delegation closed and
continue only with safe parent work or report the limitation. Never silently
substitute a model, effort, role, or fabricated tool. After dispatch, inspect realized
settings when available. On a mismatch, stop affected work and withhold acceptance
until the routing discrepancy is resolved and the result reverified. When realized
settings are unobservable, label them unconfirmed; do not claim a routing guarantee
or accept routing-sensitive work that requires that evidence. Introspection may clarify an
omitted runtime field; it cannot replace an available public contract.

Use the bounded delegation contract in the routing policy: OBJECTIVE, OWNERSHIP,
INTERFACES, CONSTRAINTS, APPLICABLE SKILLS / WORKFLOWS (when selected), VERIFICATION, and
RETURN CONTRACT. Delegates must preserve others' edits, never silently widen scope,
and return architecture/API/schema/security or cross-owner decisions to Astra.

Before implementation or delegation, check the session's available skills. When
`agent-skills` is available, automatically select, read, and apply its minimal
relevant subset without requiring another user prompt. Reassess when the work phase
changes; do not load the entire collection or impose its full lifecycle on every task.
Briefly name the selected skills when first used. For delegated work, include the
applicable skill names, discovered locations, and relevant requirements in the task
contract so the delegate reads and applies them. Other compatible installed skills
may also guide HOW the work is performed.
The plugin determines WHAT, WHO, model, ownership, coordination, and acceptance.
No external skills, including `agent-skills`, are required, installed automatically,
or vendored. If unavailable or irrelevant, silently skip this integration and use
the built-in contracts normally, without installation requests or extra confirmation.

## Risk-routed fresh review

Astra inspects the complete accumulated diff and runs appropriate requested checks.
Trivial work may omit independent review when that verification is sufficient.
Otherwise choose a fresh read-only reviewer by risk: low -> Luna / Max;
normal -> Terra / High; high -> Sol / High. Exceptional risks (security boundaries,
destructive migrations, integrity, concurrency, distributed consistency) require an
explicit Astra decision about stronger or additional independent scrutiny. No
automatic Astra reviewer is required. Fresh context and sufficient capability matter.
Use explicit controls and give the reviewer the actual change set and evidence:

~~~text
CODEX ORCHESTRATOR REVIEW
VERDICT: ship | fix-first | rethink
REASON: <evidence-based reason>
FINDINGS: <precise findings or none>
RESIDUAL RISK: <remaining risk or none>
~~~

When independent review is required, accept only after the fresh reviewer returns `ship`.
After `fix-first`, Astra classifies the findings and assigns the correction using
the [correction routing policy](references/routing-policy.md#correction-routing):
retain the current implementer for bounded fixes, select another capable model when
new evidence shows the current capability is insufficient, or correct directly for
architectural work or a minimal fix whose handoff would cost more than execution.
Astra then verifies again and obtains a new fresh review. A reviewer remains
read-only and never fixes its own findings.

Use native Codex subagents in the ChatGPT app when the exposed interface supports the
needed controls. Separate app tasks require an explicit user request. For an explicit
Codex app task, `mcp__codex_app__create_thread` supports `model` and `thinking`; call
`mcp__codex_app__list_projects` first for project targets, using a worktree by default
for Git projects and local otherwise. ChatGPT Work cloud `create_thread` must omit
`model` and `thinking`, so it cannot currently promise arbitrary model or effort
control; do not dispatch a model-pinned request there by default or use an API-key/CLI
workaround. Use a future native work tool only when its schema exposes the required
controls.

## Live delegation and completion receipts

Automatically show a short user-visible lifecycle update for **every** delegation,
including reviews, before dispatch and on completion or failure. Before dispatch,
include task name, exact bounded ownership, requested model and effort, and the
reason for that selection. On return, include agent ID, actual status, and observed
model/effort with their evidence source; if unavailable say `unobservable`. If they
differ from the request, show both. A submitted request is not runtime confirmation.
Keep progress readable; report meaningful changes without polling narration.

At task completion, emit an `API-EQUIVALENT COST RECEIPT` only when verified token
usage is available for a clearly identified scope or the user requests the receipt.
If neither condition holds, silently omit accounting output and skip the calculator;
do not search for telemetry or request setup solely to produce a receipt. If the
user requests it without observable usage, explain that it is unavailable.
Use the calculator described in the operations reference when data is available.
Capture usage already exposed by native tools with its source, unique call IDs,
agent identity, and scope as work runs.
Include parent, implementers, and all reviewers before claiming whole-task coverage.
Do not invent token counts, missing rates, or success percentages. Unknown is not zero.

Distinguish observed tokens from pricing estimates and partial coverage. Show routed
USD and the same observed tokens repriced at Astra only when comparable; label the
difference a **same-token API price comparison**, never measured all-Astra behavior,
actual net task savings, subscription charges, or improved quality/speed. If parent
usage is missing, label any available delegated-only comparison separately. With no
subagents there are no delegation savings. Effort is metadata, not a price multiplier.
Use the versioned snapshot and disclose its date and promotional Sol pricing. Reject
unsupported pricing regimes rather than silently using standard rates. An illustrative
fixture is optional and must remain separate from this task's receipt.
