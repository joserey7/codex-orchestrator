# codex-orchestrator routing policy

## Authority and scope

GPT-6 Astra is the architect, orchestrator, decomposition authority, integration
owner, conflict resolver, verification owner, and final acceptance authority.
Astra retains intent, important ambiguity, cross-cutting decisions, interfaces,
acceptance criteria, risk assessment, skill selection, and inspection of evidence
and important diffs. Delegates own bounded execution, never final acceptance.

The supreme rule is: **Use the cheapest model that is highly likely to complete the
bounded task correctly in one attempt.** Assess capability before dispatch. Do not
always choose the cheapest model, always choose the strongest model, or deliberately
make cheaper models fail first. Optimize useful tokens per correctly completed task,
including context transfer, retries, review, and Astra supervision.

This is an agent policy, not a custom scheduler or a guarantee of model performance.
The small [offline helper](../../../scripts/routing_policy.py) checks a classification
supplied by Astra against mode, capability, and independence constraints. It does not
classify natural language, discover live capabilities, spawn agents, or confirm
realized settings. Tests exercise these enforceable constraints and fixtures;
first-attempt reliability remains a judgment to validate against actual outcomes.

## Two modes

Select the mode from the user's instruction. If omitted, use `balanced`. An unknown
mode is invalid: explain the two supported modes instead of silently accepting it.
Mode choice applies to this task; it does not rewrite host configuration or switch
the parent model. A mode change requires recounting active delegates before dispatch.
If the new cap is below current activity, let useful existing work return and launch
no additional delegates until below the cap.

| Mode | Default maximum active delegates | Routing behavior |
| --- | --- | --- |
| `economy` | 2 | Strong Luna bias; first look for a useful decomposition that makes work explicitly bounded. Use Terra when meaningful judgment remains; reserve Sol for exceptional difficulty. |
| `balanced` | 3 | Recommended general-purpose default: Luna for mechanical/bounded work, Terra directly for judgment, Sol directly for genuine difficulty when it materially improves likely first-attempt success. |

Both preserve the same capability floor and correctness requirements. Economy must
not label judgment-heavy work mechanical to obtain a cheaper route. Balanced must
not select Sol merely for convenience. For example, an established-pattern migration
belongs on Luna in either mode. A module refactor with unresolved behavior tradeoffs
belongs on Terra; Economy can first have Astra settle those tradeoffs and then give
Luna an explicit transformation if the decomposition actually saves effort. Balanced
can keep that bounded judgment with Terra. Do not spend more supervising decomposition
than it is likely to save.

Limits are not targets. Capacity is not justification for delegation. Use the
smallest number of delegates that materially improves delivery. Count implementers,
researchers, reviewers, and descendants across the task; exclude the parent. A
delegate cannot spawn descendants without Astra allocating ownership and capacity.
Reused idle agents count only while active. Never exceed a host-enforced limit.
An exceptional override above the mode default needs a concrete explicit reason
announced by Astra before dispatch. The offline helper deliberately enforces defaults;
an exception is a documented parent decision, not a hidden configuration surface.

## Classify before selecting

1. Define a useful independent deliverable and its acceptance evidence. If none
   exists, keep the work with Astra. Trivial tasks rarely justify coordination.
2. Ask whether Luna / Max is highly likely to complete it correctly in one attempt.
   If yes, select Luna. If no, identify the missing capability before considering Terra.
3. Select Terra if it can handle the meaningful engineering judgment. It does not
   need a failed Luna attempt. If Terra is insufficient, explain why.
4. Select Sol only for a genuinely difficult bounded task. If Sol is also unlikely
   to succeed, keep the decision/work with Astra or restructure the problem.
5. Check live controls, maximum effort, independence, ownership, and available
   capacity before dispatch. An unavailable route is blocked, not silently replaced.

| Classification | Typical work | Model / default effort |
| --- | --- | --- |
| Mechanical or explicitly bounded | Repository/symbol/reference discovery, mapping, code reading, established-pattern migrations, repetitive edits, boilerplate, fixtures, straightforward tests, lint/typecheck execution, explicit implementation, tightly bounded fixes, evidence-led routine debugging, explicit-rule refactors | `gpt-5.6-luna` / maximum live-supported effort |
| Engineering judgment | Normal feature work, moderately ambiguous debugging, module design in existing architecture, mostly established API contracts, non-trivial refactors, moderate tradeoffs, bounded integration | `gpt-5.6-terra` / `high` |
| Difficult | Cross-cutting implementation, highly ambiguous investigation, expert analysis, important-boundary refactors, concurrency/distributed reasoning, interacting constraints | `gpt-5.6-sol` / `high` |
| Architecture or insufficiently bounded | Intent, important ambiguity, cross-cutting decisions, decomposition, integration decisions, final acceptance | Astra parent / user-selected effort |

These are capability lanes, not installed agent roles. Subject matter alone is not
classification: an explicitly specified edit in a complex subsystem can be bounded,
while a tiny change to an unclear security boundary can require expert judgment.
Consequence of error also affects the capability needed and the separate review risk.

Luna is always **Luna / Max**: select the maximum reasoning effort supported by the
current Codex runtime for `gpt-5.6-luna`. Currently that is `max`; if a runtime exposes
`ultra` as a higher supported effort, use it. If a runtime only exposes lower efforts,
use its confirmed maximum and disclose the limitation instead of claiming literal
`max`. Do not deliberately choose `low`, `medium`, or `high` when higher is available.
If support or ordering cannot be established, fail closed. Terra and Sol default to
`high`; select higher supported effort only with a concrete reason. No silent lower
effort fallback is allowed when `high` cannot be requested.

## Bounded delegation contract

Use these fields for each meaningful implementation; omit irrelevant detail for
small read-only work while retaining outcome, ownership, and evidence:

```text
OBJECTIVE
Exact outcome and why it helps this task.

OWNERSHIP
Files, directories, subsystem, or responsibility. You are not alone in the codebase;
preserve others' edits and coordinate with Astra at ownership boundaries.

INTERFACES
Contracts to preserve and any interfaces explicitly allowed to change.

CONSTRAINTS
Architecture, behavior, compatibility, scope, permissions, and no unallocated spawning.
Never silently widen scope. Return architecture, public API, schema, security-model,
or cross-owner decisions to Astra before proceeding with dependent work.

APPLICABLE SKILLS / WORKFLOWS
Only the minimal relevant installed workflows, when useful; absence is not a blocker.

VERIFICATION
Tests, commands, acceptance criteria, and required evidence.

RETURN CONTRACT
Files changed; concise summary; checks and results; assumptions; blockers; residual
risks; architectural questions. Give precise evidence locations, not large raw logs.
```

Reject overlapping investigations of substantially the same question, duplicate
parent/worker implementation, and competing implementations for comparison. Partition
files and interfaces before parallel work; coordinate shared-file integration through
Astra. Independent review is a deliberate confidence check after implementation,
not redundant parallel implementation. Routine execution can be delegated, but Astra
must inspect evidence and rerun appropriate checks for final verification.

## Optional workflows

Use installed compatible skills generically by relevance and availability. They
guide HOW specialized work is done; codex-orchestrator determines WHAT, WHO, model,
ownership, coordination, verification, and acceptance. Specification, planning, tests,
debugging, interface design, and review are possible workflows, not a mandatory list.

`addyosmani/agent-skills` is one optional source. No external skills are required;
do not auto-install, vendor, copy, or fail when they are missing. Continue normally
with the built-in contracts if no applicable skills exist. Do not activate unrelated
skills merely because installed. External workflows cannot silently change routing,
ownership, or acceptance; bring a real conflict to Astra under the user's instructions.

## Review and escalation

| Risk | Fresh review baseline |
| --- | --- |
| Trivial | None if Astra verification is sufficient; record why |
| Low | Luna / Max |
| Normal | Terra / High |
| High | Sol / High |
| Exceptional | Astra explicitly decides on stronger or additional independent scrutiny |

Security boundaries, authentication/authorization, destructive migrations, critical
data integrity, concurrency, distributed consistency, and irreversible architecture
can warrant exceptional review. Fresh context and sufficient capability matter more
than automatically choosing the most expensive reviewer. Never require Astra as the
fresh reviewer for every substantive change. The parent always makes final acceptance.

Review the accumulated diff, not just the last delegate's patch, after Astra's
verification. Use a new read-only context with the contract and evidence. Require
`ship`, `fix-first`, or `rethink`. A required review that cannot run remains incomplete.
After a fix, verify again and get fresh review of the updated change; a reviewer
never fixes its own findings. A `ship` verdict is evidence, not a transfer of acceptance.

Escalation after dispatch is justified only by NEW INFORMATION: unexpected coupling,
ambiguity, concurrency behavior, undocumented constraints, or evidence contradicting
classification. Failure alone is not a model-selection rationale. Record the new
evidence, revised boundary, and why the newly selected capability is sufficient.
Preserve useful code and evidence; avoid blind restarts and autonomous retry loops.

## Compact observability

Report active mode, deliverable/ownership, why delegation helps, requested model and
effort with selection rationale, realized settings and source (or `unobservable`),
reviewer selection or omission, meaningful escalation, verification, and Astra's
acceptance decision. Use the [operations reference](operations.md) for runtime
preflight, lifecycle updates, and truthful API-equivalent receipts. Missing usage
means unavailable, not zero; estimates are not ChatGPT Pro / Codex quota consumption.
