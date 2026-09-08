# Routing policy

## Authority

GPT-6 Astra owns architecture, important ambiguity, decomposition, interfaces, integration, risk decisions, verification and final acceptance. Delegates own bounded execution only. The supreme rule is: **select the cheapest model highly likely to complete the bounded task correctly on the first attempt**. Do not force cheaper-model failures first and do not delegate merely because capacity exists.

Astra Low is the recommended starting effort for the parent, but the user's selected parent effort is authoritative. The plugin never mutates it.

## Modes and model lanes

| Classification | Economy | Balanced |
| --- | --- | --- |
| Mechanical | Luna / Medium | Luna / maximum individual |
| Bounded | Luna / maximum individual | Luna / maximum individual |
| Judgment | Astra resolves/decomposes; if genuinely bounded route Luna; Terra only by explicit exceptional authorization | Terra / High, with a concrete capability reason |
| Difficult | Astra parent; fresh Astra / Low delegate only when separate context/parallelism justifies the handoff | Astra parent; same exception |
| Architecture/acceptance | Astra parent | Astra parent |

Economy has at most 2 active delegates; balanced at most 3. A lower host limit wins. Capacity is not justification for delegation. `maximum individual` excludes Ultra when Ultra changes topology by enabling autonomous delegation. Do not grant descendants without Astra allocation.

Sol is not a default lane. It is available only through an explicit **user** override containing model, supported effort and reason. This keeps it available for experiments without creating a permanent routing category. Explicit user model/effort requests override mode defaults when the host supports them, except they cannot transfer final architectural/acceptance authority away from Astra.

Economy may exceptionally authorize Terra / High for bounded judgment when Astra explicitly records why decomposition would cost more than the handoff. This is an exception, not a hidden lane. A user may explicitly override Luna effort for an experiment; otherwise Luna uses the mode policy.

## Classification and state

1. Define a useful deliverable and acceptance evidence. Redundant/non-useful work is `skip`.
2. Decide whether it can be bounded for delegation. If not, it is `parent` work.
3. Decide readiness and dependencies. Not-ready work is `wait`.
4. Classify capability before selecting a model. No failure ladder.
5. Decide whether it is safe to run concurrently. A serial task can remain delegable and wait until prior work completes.
6. Check mode/host capacity. Full capacity is `wait`, never an automatic parent takeover.
7. Check live model/effort/fresh-context controls and their evidence source. Missing required controls is `blocked`.
8. Dispatch only after ownership, interfaces, constraints and verification are explicit.

The offline `scripts/routing_policy.py` checks caller-supplied classifications; it does not understand natural language, discover live capabilities, dispatch agents, or prove realized settings.

## Delegation contract

Each meaningful handoff states:

- **OBJECTIVE**: one useful outcome.
- **OWNERSHIP**: relative file/directory scopes or responsibility; one writer per overlapping scope.
- **INTERFACES**: contracts to preserve/change.
- **CONSTRAINTS**: behavior, compatibility, permissions, no unallocated descendants, no silent scope expansion.
- **APPLICABLE SKILLS / WORKFLOWS**: minimal installed workflows when relevant; optional.
- **VERIFICATION**: commands, tests, reproduction or evidence.
- **RETURN CONTRACT**: concise changed files/findings, checks, assumptions, blockers and residual risks; avoid raw logs/full files.

## Risk is separate from implementation difficulty

A mechanical change can be high consequence. Record risk independently. Exceptional risk requires an explicit Astra decision before dispatch/acceptance. Fresh review baseline is:

| Risk | Economy | Balanced |
| --- | --- | --- |
| Trivial | no independent review if parent verification is sufficient and omission is recorded | same |
| Low | Luna / maximum individual | Luna / maximum individual |
| Normal | Astra / Low | Terra / High |
| High | Astra / Low | Astra / Low |
| Exceptional | Astra decides stronger/additional scrutiny | same |

A reviewer is a new read-only context, never the parent or an implementer/correction owner, and reviews the exact current accumulated diff/revision. Same-model fresh review provides context independence, not guaranteed error independence. A current `ship` verdict is evidence; Astra retains acceptance.

`fix-first` routes corrections by the new evidence: reuse a capable implementer for bounded corrections, choose a different sufficient capability only when findings show a gap, or let Astra resolve architectural/minimal corrections when handoff would cost more. Every edit invalidates the prior verdict and requires re-verification plus a fresh review when review is required. `rethink` means replan first. Repeated findings require cause/contract/capability reassessment, not an unchanged retry.

## Coordination ledger and budgets

For non-trivial/consequential work, keep a compact declared task state (see `examples/task-state.json`) and optionally validate it with `scripts/task_state.py`. Track current accumulated revision, requested/observed settings and source, task IDs, dependencies, ownership, status, concise evidence, current review verdict and a pre-dispatch budget for dispatches/corrections/reviews.

The validator is advisory consistency checking, not runtime enforcement. It cannot prove that a model ran, that a sandbox was read-only, or that a revision identifier covers dirty work; use authoritative native evidence. Unobservable realized settings remain unconfirmed. If routing proof is explicitly required, unobservability blocks that guarantee; otherwise disclose it without inventing confirmation.

A budget overrun means reassess and explicitly revise the plan. It never permits incomplete acceptance. Required failed/interrupted work must be completed by an explicitly identified replacement or remain incomplete. Optional unfinished work needs a disposition.

## Optional workflows

Installed engineering skills such as `agent-skills` may guide HOW a deliverable is executed. Select only the minimal relevant subset, pass applicable requirements to delegates, and reassess at phase changes. They do not silently change routing, ownership or acceptance. No external skill is required or auto-installed.
