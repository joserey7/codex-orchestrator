# codex-orchestrator

**GPT-6 Astra decides and accepts. Luna executes explicit work, Terra handles engineering judgment, and Sol handles difficult bounded work.**

codex-orchestrator is a public MIT-licensed Codex plugin evolved from Astra Advisor. Select the cheapest model highly likely to complete a useful bounded deliverable correctly on the first attempt. Optimize correctly accepted work, not delegate count or an unmeasured subscription-saving percentage.

## Model topology

Models describe capability; roles describe responsibility. Select directly, not through a failure ladder.

```text
                         GPT-6 ASTRA (parent)
            Intent / Architecture / Contracts / Coordination
                                   |
                 +-----------------+-----------------+
                 |                 |                 |
           GPT-5.6 LUNA      GPT-5.6 TERRA      GPT-5.6 SOL
           Explicit work    Local judgment    Difficult bounded work
                 |                 |                 |
                 +-----------------+-----------------+
                                   |
                     ASTRA INTEGRATION + VERIFICATION
                                   |
                     FRESH REVIEW (selected by risk)
                                   |
                        ASTRA FINAL ACCEPTANCE
```

The branches are choices, not mandatory agents or an escalation sequence. Astra retains architectural authority even when a specialist implements a difficult change.

### Execution modes

| Work | Economy | Balanced |
| --- | --- | --- |
| Mechanical discovery / routine commands | Luna / Medium | Luna / Max* |
| Explicit bounded implementation / validation | Luna / Max* | Luna / Max* |
| Meaningful local engineering judgment | Astra bounds or retains; **Terra / High exceptionally** | **Terra / High** |
| Difficult but bounded execution | Astra bounds or retains; **Sol / Medium exceptionally** | **Sol / Medium** |
| Architecture / important ambiguity / unbounded work | Astra parent | Astra parent |

```text
ECONOMY                              BALANCED
Astra parent                         Astra parent
  +-- Luna Medium: mechanical          +-- Luna Max*: mechanical / bounded
  +-- Luna Max*: bounded               +-- Terra High: local judgment
  +-- Terra High: justified exception  +-- Sol Medium: difficult bounded
  +-- Sol Medium: justified exception
```

Economy allows at most **2 active delegates**; balanced **3**, or a lower host limit. These are limits, not targets. Economy Terra/Sol execution requires Astra to state why further decomposition or parent execution is less useful than the bounded handoff. Balanced requires a concrete capability reason, not a failed cheaper-model attempt. Sol is a normal balanced lane, not user-override-only.

*Max means the highest confirmed **individual** reasoning effort, currently requested as `max` where supported. Do not automatically treat Ultra as a bigger Max if it also enables autonomous descendants. The default policy excludes it; topology changes need a separate explicit decision and confirmed controls.*

**Astra Low is the recommended parent starting point, not an imposed setting.** The user's chosen effort is preserved. An additional Astra specialist is exceptional and needs a reason why separate context/parallelism is worth the handoff; it is not the automatic step after Sol.

## Execution roles

**Roles do not imply models. Mode and capability select execution models; risk selects the reviewer.**

| Logical role | Responsibility | Boundary |
| --- | --- | --- |
| Explorer | Map repository files, symbols, flows and relevant tests | Read-only evidence; no architecture changes |
| Researcher | Gather external/version-specific primary evidence | Read-only findings; Astra decides implications |
| Worker | Implement a bounded change | Explicit write ownership and preserved interfaces |
| Tester | Reproduce behavior, execute checks, add targeted regression tests when authorized | Produces evidence; does not accept the change |
| Reviewer | Independently challenge the verified candidate | New read-only context; never fixes its findings |

These are logical contracts, not installed model-pinned role TOMLs. A Worker, Explorer or Tester can need Luna, Terra or Sol depending on its actual capability requirement. Read-only work is not automatically mechanical.

Use only roles that help. **Worker + Tester may be one agent** for a small explicit change; it counts as one dispatch and is not an independent review. Separate a Tester when reproduction/validation benefits from its own context. Do not create every role by default, reuse the tester as the fresh reviewer, or duplicate the parent's work.

### Delivery flow

```text
Astra understands the goal and scopes useful discovery
    |
Optional Explorer / Researcher -> Astra resolves decisions and contracts
    |
Worker -> Tester (or one Worker + Tester)
    |
Astra integrates the accumulated diff and verifies the candidate
    |
Fresh read-only Reviewer, selected by risk
    +-- fix-first -> bounded correction -> Astra re-verifies -> NEW review
    +-- rethink   -> Astra replans -> execution -> verification -> NEW review
    +-- ship      -> Astra final acceptance of the SAME verified revision
```

Parallelize only independent work. Testing a worker's final patch waits for that patch; a reviewer waits for Astra's integration/verification. Tester evidence does not replace parent verification. After `ship`, Astra checks the revision, findings and acceptance criteria without rerunning everything solely for ceremony. **Any edit invalidates prior verification/review for acceptance**: verify the updated candidate and obtain a new fresh review when required.

## Fresh review by risk — identical in both modes

| Risk | Fresh reviewer |
| --- | --- |
| Trivial | May omit if Astra verification is sufficient; record why |
| Low | Luna / Max* |
| Normal | Terra / High |
| High | Sol / High |
| Exceptional | Astra / Low in a fresh context, after an explicit parent risk decision |

Implementation difficulty and consequence of error are independent. **Sol Medium implementation is not Sol High review.** Economy changes the execution strategy, not the review standard for the same risk. Exceptional security/integrity/concurrency/destructive-change risk can require stronger or additional scrutiny chosen explicitly by Astra. A justified stronger reviewer is allowed; silently weakening the baseline is not.

Same-model fresh review gives context independence, not guaranteed error independence. Astra always retains final acceptance.

## Install

```text
codex plugin marketplace add joserey7/codex-orchestrator --ref main
codex plugin add codex-orchestrator@codex-orchestrator
```

For an unreleased checkout, replace the marketplace source with `.` and run from the repository root. Start a fresh task after installing/upgrading. Select GPT-6 Astra as the parent; the skill cannot change the parent model/effort.

```text
Use $codex-orchestrator:orchestration in balanced mode to implement this feature.
Use $codex-orchestrator:orchestration in economy mode to fix this bounded bug.
```

Python 3.11+ is required for repository verification/offline helpers; 3.12 is recommended. Core orchestration uses native host tools. The package targets Windows, Linux and macOS; actual model-pinned subagent support depends on client/version/account capabilities.

## Coordination and runtime honesty

`delegate` dispatches selected bounded work; `parent` means work genuinely belongs to Astra; `wait` preserves delegation pending capacity/dependencies/serialization; `skip` avoids redundant work; `blocked` reports missing controls/evidence/authorization. Full capacity never silently transfers a cheap task to Astra.

Partition writers by file/directory scope, keep reports concise, and set pre-dispatch budgets for dispatches/corrections/reviews. Overruns trigger reassessment, never permission to accept incomplete work. Installed compatible engineering skills guide HOW; `agent-skills` remains optional and is not auto-installed.

Live native schemas and metadata outrank static documentation. Require explicit model/effort/fresh-context controls. Requested settings are not proof of realized settings. Mismatches stop affected work; unobservable settings remain unconfirmed and block claims requiring routing proof.

`scripts/task_state.py` validates declared roles, dependencies, ownership, capacity, budgets, requested/observed settings, pre-review verification evidence and current-revision acceptance. It is **not a scheduler, runtime interceptor or proof of model/sandbox execution**. See [routing policy](plugins/codex-orchestrator/skills/orchestration/references/routing-policy.md) and [operations](plugins/codex-orchestrator/skills/orchestration/references/operations.md).

## Accounting and evaluation

API-equivalent accounting remains outside the installed plugin and normal task context. The historical upstream calculator under `tools/accounting/` is for manual/reference use; it does not measure ChatGPT Pro/Codex quota.

The optional [evaluation guide](plugins/codex-orchestrator/skills/orchestration/references/evaluation.md) describes repeatable comparisons when trustworthy telemetry is already available. Unknown usage is not zero. Client/version smoke evidence is separate from offline CI; no subscription-saving percentage is claimed.

## Development

```text
python plugins/codex-orchestrator/scripts/verify.py
```

CI runs Python 3.11/3.12 on Ubuntu and 3.12 on Windows/macOS. Tests cover routing, logical roles, the shared risk-review matrix, lifecycle/acceptance consistency, package contracts and the separately preserved historical accounting tests. Offline tests do not establish natural-language classification quality, live model pins or savings.

## Acknowledgements and license

- [DannyMac180/astra-advisor](https://github.com/DannyMac180/astra-advisor) is the primary upstream/fork foundation: Astra authority, native delegation/evidence safeguards and the historical accounting utility.
- [DannyMac180/sol-advisor](https://github.com/DannyMac180/sol-advisor) inspired bounded capability delegation, selective review and parent acceptance.
- [donvito/codex-astra-luna-orchestrator](https://github.com/donvito/codex-astra-luna-orchestrator) inspired Explorer/Researcher/Worker/Tester roles, concise returned context and inexpensive execution. This plugin keeps roles independent from model selection.
- [addyosmani/agent-skills](https://github.com/addyosmani/agent-skills) inspired optional structured engineering workflows.

These relationships do not imply endorsement. Preserve upstream MIT code and Daniel McAteer's copyright/permission notice in root and installed-package LICENSE files. Other projects are conceptual inspiration; do not copy their source without reviewing their licenses.
