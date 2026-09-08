---
name: orchestration
description: "Use codex-orchestrator for economy or balanced delivery: Astra owns decisions and acceptance; logical execution roles use capability-routed Luna, Terra and Sol."
---

# codex-orchestrator

GPT-6 Astra owns intent, architecture, important ambiguity, decomposition, interfaces, integration, risk decisions, conflict resolution, verification and final acceptance. Preserve the user's parent model/effort. **Astra Low is a recommended starting point, not an enforced setting.**

Before first dispatch read [routing policy](references/routing-policy.md). Read [operations](references/operations.md) when live dispatch/review details are needed, not optional accounting during normal work.

Emit one compact plan before substantive work:

```text
CODEX ORCHESTRATOR ROUTE
parent: <requested/observed model and effort; unobservable when needed>
mode: <economy|balanced>
plan: <useful roles, bounded deliverables and selected capabilities>
risk: <consequence-of-error and independent review plan>
```

## Capability routing

Classify before dispatch; never build a Luna -> Terra -> Sol -> Astra failure ladder.

| Work | Economy | Balanced |
| --- | --- | --- |
| Mechanical discovery / routine commands | Luna / Medium | Luna / maximum individual |
| Explicit bounded implementation / validation | Luna / maximum individual | Luna / maximum individual |
| Meaningful local engineering judgment | Astra bounds/retains; Terra / High only with an explicit exception reason | Terra / High with a capability reason |
| Difficult but bounded work | Astra bounds/retains; Sol / Medium only with an explicit exception reason | Sol / Medium with a capability reason |
| Architecture / important ambiguity / unbounded work | Astra parent | Astra parent |

Sol / Medium is a normal balanced execution lane, not user-override-only. In Economy, Astra must explain why further decomposition or parent work would be less useful than a Terra/Sol handoff. Do not overspecify work merely to force Luna. A separate Astra specialist requires an explicit supported model/effort and reason why fresh context/parallelism is worthwhile; it never inherits architectural authority.

`maximum individual` means the highest confirmed individual reasoning effort. Exclude Ultra from automatic selection when it changes topology; do not grant descendants without an explicit allocation. Missing controls/models/efforts block the route, never silently substitute.

## Logical execution roles

Roles do not pin models. Mode and capability select execution models; risk selects the Reviewer.

- Explorer: read-only repository mapping, symbols, flows and test locations.
- Researcher: read-only external/version-specific primary evidence.
- Worker: bounded implementation under explicit write ownership.
- Tester: reproduction, checks and authorized regression tests; returns evidence, not acceptance.
- Reviewer: a separate fresh read-only context after Astra verifies the integrated candidate.

Use only helpful roles. Combine Worker + Tester for small explicit changes, counting one dispatch. Separate a Tester when its context adds value. No fixed role TOMLs and no mandatory explorer/worker/tester sequence. Do not reuse any execution context as the fresh reviewer. Read-only research or test diagnosis may itself need Terra/Sol; a role name is not a capability classification.

## Coordination

`delegate` dispatches selected work; `parent` is genuine Astra work; `wait` preserves delegation pending capacity/dependencies/serialization; `skip` avoids redundant/non-useful work; `blocked` reports missing controls/evidence/authorization. Never turn full capacity into Astra execution.

Use at most 2 active delegates in economy, 3 in balanced, or a lower host limit. Include reviewers/descendants; limits are not targets. Parallelize only independent work with one writer per file/subsystem. Validation of a final patch waits for that patch. Avoid duplicate investigation and competing implementations.

A meaningful handoff states ROLES, OBJECTIVE, OWNERSHIP, INTERFACES, CONSTRAINTS, optional applicable workflows, VERIFICATION and a concise RETURN CONTRACT. Delegates preserve others' edits, do not widen scope and return architecture/API/schema/security/cross-owner decisions to Astra.

Use the minimal relevant installed engineering skills before implementation/delegation. They guide HOW; this plugin owns WHAT/WHO/model/coordination/acceptance. `agent-skills` is optional and never auto-installed.

## Verification, review and acceptance

Consequence-of-error is separate from implementation difficulty. The **review baseline is identical in both modes**:

| Risk | Fresh reviewer |
| --- | --- |
| Trivial | May omit when parent verification suffices; record why |
| Low | Luna / maximum individual |
| Normal | Terra / High |
| High | Sol / High |
| Exceptional | Astra / Low fresh context after an explicit parent risk decision |

Exceptional risk can require stronger/additional scrutiny. A stronger reviewer needs an explicit reason; never silently weaken the baseline. Reviewer selection does not require an Economy execution exception.

The lifecycle is **execution -> Astra integration/verification -> fresh review -> Astra final acceptance**. The Tester supplies evidence; Astra inspects the accumulated diff, confirms acceptance criteria and runs/confirms highest-value checks BEFORE dispatching review. Do not duplicate every test or investigation unnecessarily.

The fresh reviewer receives the exact verified revision and parent verification evidence, stays read-only and returns `ship`, `fix-first` or `rethink`. Never fix your own review findings. Every edit invalidates previous verification/review for acceptance. `fix-first`: route bounded corrections to a capable owner, Astra re-verifies, then NEW fresh review. `rethink`: Astra replans first. Persistent findings trigger reassessment, not unchanged retry. After `ship`, Astra accepts the same revision after checking findings and evidence, without gratuitous full re-verification.

## Evidence

Native schemas/runtime metadata outrank static documentation. Record explicit model/effort/fresh-context controls and their source before dispatch. Requested settings are not proof of realized settings. Mismatches stop affected work. Disclose unobservable settings; they block guarantees requiring routing proof.

Use `scripts/task_state.py` for non-trivial/consequential declared-state checks. It validates roles, dependencies, ownership, budgets, pre-review verification evidence and current-revision acceptance, not runtime truth or sandbox isolation. Set small pre-dispatch budgets; overrun means explicit reassessment, never incomplete acceptance.

See [operations](references/operations.md) for evidence records and optional [evaluation](references/evaluation.md) for benchmarks. Cost/accounting is not part of normal orchestration.
