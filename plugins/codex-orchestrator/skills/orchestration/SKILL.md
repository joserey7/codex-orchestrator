---
name: orchestration
description: "Use codex-orchestrator for economy or balanced delivery: Astra owns decisions and acceptance; cheaper capable models execute bounded work."
---

# codex-orchestrator

GPT-6 Astra is the parent architect and acceptance owner. Preserve the parent model and effort selected by the user; the plugin never changes them. **Astra Low is the recommended starting point, not an enforced setting.** Astra owns intent, architecture, important ambiguity, decomposition, interfaces, integration, risk decisions, conflict resolution, verification and final acceptance.

Before first dispatch, read [routing policy](references/routing-policy.md). Read [operations](references/operations.md) only when live dispatch/review details are needed. Do not load optional accounting during normal work.

Emit one compact plan before substantive work:

```text
CODEX ORCHESTRATOR ROUTE
parent: <requested/observed model and effort; say unobservable when needed>
mode: <economy|balanced>
plan: <bounded deliverables and selected routes>
risk: <task-specific risk and review plan>
```

## Core model policy

Classify before dispatch. Never build a Luna -> Terra -> Astra failure ladder.

| Work | Economy | Balanced |
| --- | --- | --- |
| Mechanical/read-only discovery, routine commands | Luna / Medium | Luna / maximum individual reasoning |
| Explicit bounded implementation/debugging/refactor | Luna / maximum individual reasoning | Luna / maximum individual reasoning |
| Meaningful local engineering judgment | Astra resolves/decomposes, then Luna if the result is truly bounded; exceptional Terra needs an explicit reason | Terra / High with a concrete reason Luna is insufficient |
| Difficult/architectural/important ambiguity | Astra parent | Astra parent |

`maximum individual reasoning` means the highest confirmed individual effort. Do **not** treat `ultra` as merely above Max: if Ultra also enables autonomous descendants, it requires a separate explicit user decision and is outside the default lanes. Delegates may not spawn descendants without Astra allocation.

Sol is not a default lane. Use it only on an explicit user override, with an explicit supported effort and reason. Do not silently substitute unavailable models/efforts. A difficult independent deliverable may use a fresh Astra / Low delegate when Astra explicitly decides the separate context or parallelism is worth the handoff; otherwise keep it in the parent.

Economy should try to remove ambiguity cheaply, but never spend more Astra supervision decomposing work than the handoff is likely to save. Balanced selects the cheapest model that naturally fits the deliverable. Optimize correctly accepted work, not delegation count.

## Coordination states

Treat these as distinct:

- `delegate`: dispatch to the selected model.
- `parent`: Astra genuinely owns this work.
- `wait`: work is delegable but blocked by capacity/dependencies/serialization. Never transfer it to Astra merely because slots are full.
- `skip`: work is redundant or not useful. Do not perform it in the parent.
- `blocked`: a required control/evidence/authorization is missing.

Delegability and parallel safety are separate. A serial task can still be a later Luna task. Use at most 2 active delegates in economy and 3 in balanced, or a lower host limit. Limits include reviewers/descendants and are not targets. Use one writer per file/subsystem and avoid duplicate investigations or competing implementations.

For each meaningful handoff specify OBJECTIVE, OWNERSHIP, INTERFACES, CONSTRAINTS, optional applicable skills/workflows, VERIFICATION, and a concise RETURN CONTRACT. Delegates preserve others' edits, do not widen scope, and return architecture/API/schema/security/cross-owner decisions to Astra.

Before implementation/delegation, use the minimal relevant installed engineering skills when available. They guide HOW; this plugin owns WHAT/WHO/model/coordination/acceptance. `agent-skills` remains optional and is never installed automatically.

## Risk and review

Implementation capability and consequence-of-error are separate. Exceptional risk (security boundaries, destructive migrations, critical integrity, concurrency/distributed consistency, irreversible architecture) requires an explicit Astra decision even when the edit itself is mechanical.

Fresh review baseline:

| Risk | Economy | Balanced |
| --- | --- | --- |
| Trivial | May omit with a recorded reason | May omit with a recorded reason |
| Low | Luna / maximum individual | Luna / maximum individual |
| Normal | Astra / Low | Terra / High |
| High | Astra / Low | Astra / Low |
| Exceptional | Astra explicitly decides stronger/additional scrutiny | Astra explicitly decides stronger/additional scrutiny |

Reviewers are fresh and read-only, inspect the complete accumulated diff, and return `ship`, `fix-first`, or `rethink`. They never fix their own findings. Any correction invalidates the prior verdict; Astra re-verifies and obtains a new fresh review when review is required. Repeated findings trigger reassessment, not automatic escalation. Sol review remains an explicit user override.

## Evidence and acceptance

Public native tool schemas and runtime metadata outrank static snapshots. Before dispatch require explicit model, effort and fresh-context controls and record their evidence source. Requested settings are not proof of realized settings. If observed values mismatch, stop affected work and reverify. If realized settings are unobservable, disclose that; only block acceptance when routing proof is explicitly required.

Use `scripts/task_state.py` as a **declared-state consistency check** when the task is non-trivial or before a consequential acceptance. It validates dependencies, one-writer ownership, budgets, review freshness and revision matching; it does not intercept Codex or prove runtime truth.

Set a small pre-dispatch budget for dispatches, correction cycles and reviews. Exceeding it is a reassessment gate: revise the plan explicitly or stop. A budget never permits accepting incomplete work.

Astra accepts only after inspecting the complete accumulated diff/revision, running or confirming the highest-value checks, resolving required work and current review findings, and recording concise evidence. Do not redo every delegate investigation when returned evidence is sufficient.

Read [operations](references/operations.md) for live lifecycle details and [evaluation](references/evaluation.md) for optional benchmarking. Cost/accounting is not part of normal orchestration.
