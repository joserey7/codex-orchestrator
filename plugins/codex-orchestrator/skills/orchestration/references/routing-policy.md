# Routing policy

## Authority

GPT-6 Astra owns architecture, important ambiguity, decomposition, interfaces, integration, risk decisions, verification and final acceptance. Delegates own bounded execution. Select the cheapest model highly likely to complete the useful deliverable correctly on the first attempt. Do not force cheaper-model failures or delegate merely because capacity exists.

Astra Low is recommended, but the user's parent effort is authoritative. The plugin never mutates it.

## Modes and capability lanes

| Classification | Economy | Balanced |
| --- | --- | --- |
| Mechanical | Luna / Medium | Luna / maximum individual |
| Bounded | Luna / maximum individual | Luna / maximum individual |
| Judgment | Astra bounds/retains; Terra / High exceptionally | Terra / High, with a capability reason |
| Difficult bounded | Astra bounds/retains; Sol / Medium exceptionally | Sol / Medium, with a capability reason |
| Architecture / unbounded | Astra parent | Astra parent |

`difficult` means difficult but bounded, not ownership of unresolved architecture. Set `delegable=False` or classify `architecture` when no bounded contract exists. Economy Terra/Sol execution needs an explicit `economy_exception_reason`: why further decomposition or keeping the work in Astra would cost more coordination or produce a worse handoff. A capability rationale alone does not authorize an Economy exception. Balanced chooses a sufficient model directly; neither mode runs a failure ladder.

Sol is a normal balanced lane. Explicit model/effort overrides require `override_model`, `override_effort`, `override_reason` and `override_authority` (`user` or `astra`). A complete Astra-authorized Terra/Sol override can express an Economy exception. A separate Astra specialist needs an explicit reason for fresh context/parallelism; architectural and acceptance authority never leave the parent. Deliberately changing Luna's effort policy requires a user override.

Economy has at most 2 active delegates, balanced 3. A lower host limit wins. Capacity is not justification for delegation. `maximum individual` selects the highest confirmed individual effort, excluding topology-changing Ultra. No unallocated descendants, silent model/effort fallback or custom inference workaround.

## Logical roles

`roles` is an array of logical responsibilities, not native model-pinned profiles. Execution roles are `explorer`, `researcher`, `worker`, `tester`; `reviewer` is separate. Omitted roles default to Worker in the routing helper. Roles do not determine the model: mode and capability do; risk alone determines the review baseline.

Explorer maps the repository read-only. Researcher returns external/version-specific primary evidence read-only. Worker implements within write ownership. Tester reproduces behavior, runs checks and may add regression tests within explicitly owned paths. Tester findings are verification evidence, not independent review or final acceptance.

Combine `roles: ["worker", "tester"]` when one bounded implementation/test packet is sufficient; it is one dispatch. Separate a Tester when an independent reproduction/validation context adds value. No role must be spawned just because it exists. Pure exploration/research stays read-only; any implementation belongs in a separate owned work packet. Never combine Reviewer with execution or reuse an execution context as a fresh reviewer.

Discovery precedes decisions when facts are missing; Astra settles architecture/contracts before dependent implementation. Tests of the final change wait for it. Independent investigations/work streams may run in parallel; diagrams do not imply a mandatory parallel pipeline.

## Classification and routing states

1. Define a useful deliverable and acceptance evidence; redundant/non-useful work is `skip`.
2. Decide whether the work can be bounded; unbounded/architectural work is `parent`.
3. Check dependencies/readiness; not-ready work is `wait`.
4. Classify capability and select a sufficient model before dispatch.
5. Decide concurrency safety separately from delegability; serial work can remain delegated.
6. Check mode/host capacity; full capacity is `wait`, never parent takeover.
7. Require live model/effort/fresh-context controls and their source; missing requirements are `blocked`.
8. Dispatch only with ownership, contracts and verification criteria.

`scripts/routing_policy.py` is an offline check of caller-supplied classifications, not a natural-language classifier, capability detector or scheduler. Its v3 result includes roles. The old `delegate_difficult` switch is replaced by bounded `difficult` classification; request an Astra specialist through an explicit override, not that old switch.

## Delegation contract

Each meaningful handoff states ROLES, OBJECTIVE, OWNERSHIP, INTERFACES, CONSTRAINTS, optional APPLICABLE SKILLS / WORKFLOWS, VERIFICATION and RETURN CONTRACT. Own relative files/directories, preserve others' changes, do not widen scope, and return architectural/API/schema/security/cross-owner decisions to Astra. Return concise findings, paths, checks, assumptions and risks rather than raw logs or full files.

## Mode-independent review

Risk describes consequence of error, not implementation difficulty or execution role. A mechanical edit can have exceptional consequences. Both modes use exactly this baseline:

| Risk | Fresh reviewer |
| --- | --- |
| Trivial | May omit after sufficient Astra verification with a recorded reason |
| Low | Luna / maximum individual |
| Normal | Terra / High |
| High | Sol / High |
| Exceptional | Astra / Low fresh context after an explicit Astra risk decision |

Reviewer selection never needs an Economy execution exception. Sol / Medium execution must not leak into Sol / High review. Review overrides may choose a stronger model with explicit authority/reason; they must not lower the risk baseline or the selected model's review effort floor. The shared `review_meets_baseline` helper is used by routing and task-state validation. These are policy floors, not empirically guaranteed capability rankings.

Exceptional security boundaries, destructive migrations, critical integrity, concurrency/distributed consistency or irreversible decisions need an explicit Astra scrutiny plan, potentially stronger/additional review. Same-model fresh review offers context independence, not guaranteed error independence.

## Delivery lifecycle

**Execution -> Astra integration/verification -> fresh read-only review -> Astra final acceptance.**

Worker/Tester finish the candidate and return evidence. Astra integrates the full accumulated diff, inspects it and runs/confirms relevant checks and acceptance criteria before review starts. The Reviewer receives that exact revision and the parent verification evidence. It does not fix findings. Its verdict is `ship`, `fix-first` or `rethink`; a required review cannot become skipped or parent-only work.

Any edit invalidates the prior verification/review for acceptance. After `fix-first`, assign a bounded correction to a capable implementer, select another capability only when findings justify it, or let Astra resolve architectural/minimal corrections. Re-verify the updated candidate, then obtain a NEW fresh review. `rethink` requires replanning first. Persistent findings require cause/contract/capability reassessment, never unchanged retries.

After `ship`, Astra checks that the verified/reviewed revision is unchanged, required work and findings are resolved, and accepts. Do not repeat the entire verification solely to satisfy a redundant final phase.

## Declared task state and budgets

For non-trivial/consequential work maintain a compact record (see `examples/task-state.json`) and optionally validate with `scripts/task_state.py`. Track revision including dirty changes, requested/observed settings, task IDs, dependencies, roles, ownership, status, evidence and pre-dispatch dispatch/correction/review budgets.

State `kind` remains the lifecycle category: `discovery`, `research`, `implementation`, `validation`, `correction` or `review`. `roles` is separate; old records without it derive the appropriate logical role from kind. A combined Worker + Tester uses one implementation/correction record. Review records require their own new context/agent ID.

Capture `parent_verified_revision` and `parent_verification_evidence` on the Reviewer record BEFORE dispatch; the revision must match `reviewed_revision`. An active review additionally requires the current parent diff/verification evidence and no active execution writers. Old review evidence is retained after corrections, not retroactively rewritten. Current acceptance needs same-revision `ship` and parent verification/acceptance evidence.

A review using a confirmed lower Luna maximum must supply `supported_efforts` and `capabilities_source`; without those the checker only validates literal `max`. Unobservable settings remain unconfirmed and block contracts requiring routing proof. This validator checks assertions, not actual chronology, model execution, dirty-diff hashing or sandbox isolation.

Budgets count dispatches, reviews and correction cycles (including parent corrections). An overrun requires explicit reassessment/replanning, never a correctness waiver. Required failed/interrupted work needs an identified completed replacement or remains incomplete. Optional unfinished work needs a disposition.

## Optional workflows

Installed engineering skills such as `agent-skills` guide HOW work is executed. Select the minimal relevant subset, pass requirements to delegates and reassess at phase changes. They do not silently change routing, ownership or acceptance. No external skill is required or auto-installed.
