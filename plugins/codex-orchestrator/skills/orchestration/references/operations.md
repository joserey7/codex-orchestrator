# Operations

Read this when live dispatch/review details are needed. [Routing policy](routing-policy.md) owns model/role/risk selection.

## Parent and preflight

GPT-6 Astra must be the primary session for an Astra-orchestrated claim. Preserve the user's parent effort; Low is a recommendation, not an automatic change. Record observable parent settings; disclose unobservable values rather than inventing evidence.

Before dispatch inspect the current native schema. Require explicit model, supported effort and fresh-context controls and record the source. Use the exposed generic native spawn interface with explicit settings (`fork_turns: none` when that is the public field). Do not install role TOMLs that could pin a role to another model. The logical `roles` field belongs to our contract/ledger, not an invented native tool parameter.

Luna's maximum individual effort excludes a setting such as Ultra when it enables autonomous descendants. Missing/conflicting controls block the affected route; no silent model/effort substitution or separate inference mechanism workaround.

Execution defaults: Economy Luna Medium mechanical, Luna maximum-individual bounded, Terra High/Sol Medium only with explicit Astra exception reasons. Balanced Luna maximum-individual, Terra High judgment, Sol Medium difficult bounded. Unbounded decisions stay with Astra; an additional Astra specialist must justify its separate context.

## Roles and lifecycle

Explorer/Researcher collect read-only evidence when needed. Astra uses it to decide architecture and contracts. Worker implements; Tester reproduces, validates and may write authorized regression tests. Worker + Tester can share one bounded dispatch. Neither role replaces Astra verification or a fresh Reviewer.

Keep user-visible progress compact: one plan and meaningful changes unless detailed orchestration is requested. Retain task IDs, roles, ownership, dependencies, selected model/effort, control sources, observed settings and result evidence in the declared state. No polling narration or mandatory role sequence.

`wait` preserves future delegation pending readiness/capacity/serialization; `skip` avoids work. Respect economy 2 / balanced 3 active delegates and lower host limits, including reviewers/descendants. Partition writers by non-overlapping files/directories. Prefer complete verifiable deliverables over micro-delegation.

## Candidate verification before review

After execution, Astra integrates changes, identifies the accumulated revision (including dirty work), inspects the diff and checks relevant evidence/acceptance criteria. Run or confirm highest-value tests; returned Tester evidence can be reused when trustworthy, but never treat the tester's assertion as final acceptance.

Only THEN dispatch a fresh Reviewer. Freeze the candidate while it is reviewed; do not leave writers modifying it. Provide exact revision, contracts, parent verification evidence, checks and residual risks. Capture `parent_verified_revision` and `parent_verification_evidence` in the review record before dispatch, matching `reviewed_revision`.

Reviewer defaults are mode-independent: trivial may omit with reason; low Luna maximum-individual; normal Terra High; high Sol High; exceptional Astra Low after an explicit parent decision. Additional/stronger scrutiny needs an explicit reason. Do not use an Economy exception gate for normal/high reviews. A stronger review override cannot lower the risk/effort floor.

Reviewers are read-only, fresh contexts, not the parent or any earlier executor (including a read-only Tester). Do not claim enforced sandbox isolation without observed permission evidence. Return `ship`, `fix-first` or `rethink`; never implement your own findings.

## Corrections and final acceptance

Every edit invalidates verification/review for acceptance. Route `fix-first` corrections according to the evidence; reuse a capable Worker where sensible. Astra re-verifies the new candidate, then dispatches a NEW fresh Reviewer. `rethink` requires replanning. Keep prior review evidence tied to its old revision, not silently updated.

After `ship`, Astra confirms the same accumulated revision remains unchanged, required work and material findings are resolved, checks are sufficient and residual risks are recorded. Then accept; do not rerun everything solely because acceptance is a separate stage. Any subsequent integration edit restarts verification/review.

Use `scripts/task_state.py INPUT.json --acceptance` for optional assertion consistency checks. Logical `roles` may combine Worker + Tester; `kind` identifies the lifecycle record. `research` and `validation` are execution kinds, not synonyms for review. The validator does not intercept Codex or prove runtime settings/chronology.

Set pre-dispatch budgets for dispatches, corrections and reviews. An overrun means reassess and explicitly revise the plan or report a blocker, never waive correctness.

## Runtime evidence and host boundaries

Requested settings are not proof of realized settings. On observed mismatch stop affected work and reverify. Unobservable settings remain disclosed/unconfirmed and block only guarantees explicitly requiring routing proof. Record client/version during release smoke checks; cross-platform Python support does not imply every host exposes model-pinned subagents. Use only controls exposed by the current native interface. Separate app/cloud tasks require the user's explicit request.

## Accounting boundary

Accounting remains outside the installed plugin. Normal tasks do not load pricing/token instructions or emit API-equivalent receipts. Repository-root `tools/accounting/` preserves the historical upstream utility for manual/reference use, not ChatGPT Pro/Codex quota measurement.

See optional [evaluation](evaluation.md) for comparisons using already-available telemetry. Unknown usage remains unknown, never zero.
