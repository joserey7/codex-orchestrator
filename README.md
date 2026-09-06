# codex-orchestrator

**GPT-6 Astra owns architecture and acceptance. Cheaper capable models perform
bounded execution.**

codex-orchestrator is a public, open-source Codex plugin evolved from Astra Advisor.
Its central rule is to **use the cheapest model that is highly likely to complete
the bounded task correctly in one attempt**. It aims to make available Codex /
ChatGPT Pro capacity more useful without trading correctness for repeated cheap
attempts. It does not promise a particular quota saving or measured success rate.

## Install and invoke

Use a Codex CLI or desktop host with plugin support and native subagents exposing
explicit model, reasoning-effort, and clean-context controls. Install the marketplace
and plugin with the CLI:

```text
codex plugin marketplace add joserey7/codex-orchestrator --ref main
codex plugin add codex-orchestrator@codex-orchestrator
```

The remote commands install the version published on `main`. For a checkout or an
unreleased branch, run these commands from the repository root instead:

```text
codex plugin marketplace add .
codex plugin add codex-orchestrator@codex-orchestrator
```

In desktop environments, use the host's plugin installation UI if available, then
start a fresh task. Select **GPT-6 Astra** as the parent at your preferred supported
effort; a skill cannot switch the parent model. Invoke:

```text
Use $codex-orchestrator:orchestration in balanced mode to implement this feature.
```

Or conserve capacity more aggressively:

```text
Use $codex-orchestrator:orchestration in economy mode to fix this bounded bug.
```

No other third-party skills are needed. If no mode is specified, **balanced** is the
recommended default because it selects sufficient engineering capability directly
while keeping routine work on Luna. Only `economy` and `balanced` are public modes.

The package is designed for Windows, Linux, and macOS. Core orchestration uses the
host's native tools. Accounting and repository verification require **Python 3.11+**;
**Python 3.12** is recommended. There are no third-party Python dependencies. Examples
use `python`; use `python3`, `py -3.12`, or your installed interpreter path as appropriate.
Neither Bash nor PowerShell is required for shared tooling.

For updates:

```text
codex plugin marketplace upgrade codex-orchestrator
codex plugin add codex-orchestrator@codex-orchestrator
```

## Architecture and routing

```text
GPT-6 Astra: intent, architecture, decomposition, interfaces, acceptance criteria
    -> classify a useful independent deliverable before dispatch
    -> Luna / Max | Terra / High | Sol / High+
    -> Astra integration and verification
    -> risk-routed fresh review where required
    -> Astra final acceptance
```

The implementation preserves upstream native spawning, clean child context, explicit
model/effort selection, capability preflight, fail-closed safeguards, observed-setting
reporting, the review lifecycle, and API-equivalent cost accounting. The main change
is routing policy. There is no custom scheduler, nested inference CLI, database,
retry engine, or mandatory agent-role installer.

| Mode | Maximum active delegates by default | Behavior |
| --- | --- | --- |
| `economy` | 2 | Strong Luna bias; favor useful decomposition into explicit work. Terra when judgment warrants it; Sol exceptional. |
| `balanced` | 3 | Luna for mechanical/bounded work; Terra directly for normal engineering judgment; Sol directly for genuine difficulty. |

Limits include reviewers and descendants and are **limits, not targets**. Capacity
is not justification for delegation. Parallel work must be genuinely independent;
reject duplicate investigations and competing implementations. Exceptional overrides
need a concrete reason and cannot exceed host limits.

| Work requiring | Selected model | Requested reasoning effort |
| --- | --- | --- |
| Discovery, mechanical edits, explicit implementation, routine tests and fixes | `gpt-5.6-luna` | Maximum supported by the current runtime; currently `max` |
| Meaningful engineering judgment, module design, moderate ambiguity/integration | `gpt-5.6-terra` | `high` by default |
| Difficult cross-cutting work, expert investigation, interacting constraints | `gpt-5.6-sol` | `high` by default; higher when justified |
| Architecture, important ambiguity, decomposition, integration decisions, acceptance | `gpt-6-astra` parent | User-selected |

Luna always uses its live-supported maximum. Terra and Sol may use a higher supported
effort for a concrete reason. Sol needs a reason why Terra is insufficient. If even
Sol is unlikely to succeed, Astra keeps the work or decomposes it. Escalation requires
new information that changes the classification; a deliberate cheaper-model failure
ladder is prohibited.

Each meaningful delegated implementation receives an objective, ownership, interfaces,
constraints, optional applicable workflows, verification criteria, and a return
contract. Agents return concise evidence, preserve others' edits, and bring changes
to architecture, public APIs, schemas, security, or another owner's subsystem back to
Astra. Astra inspects the accumulated diff and verifies the result before acceptance.

Read the [routing policy](plugins/codex-orchestrator/skills/orchestration/references/routing-policy.md)
for examples, delegation contracts, and mode behavior, and the
[operations reference](plugins/codex-orchestrator/skills/orchestration/references/operations.md)
for the native lifecycle and evidence rules.

## Review and runtime honesty

Trivial work may omit independent review when Astra verification is sufficient.
Otherwise fresh review is selected by risk: **low -> Luna / Max; normal -> Terra /
High; high -> Sol / High**. Exceptional risks such as authorization, destructive
migrations, data integrity, or concurrency require an explicit Astra decision about
stronger or additional scrutiny. A reviewer stays read-only and returns `ship`,
`fix-first`, or `rethink`. Fixes require verification and fresh review; Astra always
retains final acceptance authority.

Live public tool schemas outrank static capability snapshots. Delegation requires
explicit supported model/effort controls and a fresh context (`fork_turns: none` on
the exposed generic native spawn interface). Missing or conflicting controls block
the affected route; the plugin reports the limitation and continues only safe parent
work. It never silently substitutes models, uses API keys, or launches nested CLI
inference as a workaround.

Requested values and runtime-observed values are reported separately. An accepted
spawn request is not proof of realized settings. Mismatches stop affected work;
unobservable settings remain unconfirmed, and work requiring verified routing cannot
be accepted without that evidence. A host without the required controls cannot
provide this plugin's model-pinned delegation workflow.

Separate desktop app tasks require an explicit user request. ChatGPT Work cloud
`create_thread` must omit `model` and `thinking` in the current schema, so it cannot
promise this model/effort routing. Native capabilities vary by host and account; see
[official subagent documentation](https://learn.chatgpt.com/docs/agent-configuration/subagents).
The current tool schema remains authoritative for actual dispatch.

## Optional engineering workflows

Installed compatible skills may guide specification, planning, testing, debugging,
interface design, or review. codex-orchestrator determines **what, who, model,
ownership, coordination, and acceptance**; an applicable workflow guides **how**.
Only use the minimal relevant subset. `addyosmani/agent-skills` is one optional
source, not a dependency. Nothing is auto-installed or vendored, and missing external
skills never block core operation. The built-in delegation contracts stand alone.

## Visibility and API-equivalent receipts

Compact updates identify the mode, bounded deliverable, selected model/effort and
reason, runtime-observed settings or their absence, reviewer, meaningful escalation,
and verification/acceptance outcome.

The preserved calculator prices observed token usage against a versioned historical
snapshot and compares the same tokens repriced at Astra. Coverage is explicitly
whole-task, delegated-only, partial, or unavailable. Missing parent/reviewer usage
prevents a whole-task claim. Unknown usage is not zero; no delegates means no
delegation savings. Reasoning effort is metadata, not a price multiplier.

**API-equivalent estimates do not equal actual ChatGPT Pro / Codex subscription
quota consumption.** They do not measure an all-Astra run, net task savings, speed,
or quality. The [September 4, 2026 snapshot](plugins/codex-orchestrator/pricing/2026-09-04.json)
is retained from upstream with its provenance; Sol pricing is promotional. Unsupported
long-context, service-tier, and cache-write regimes are rejected. The 128,000-input-token
per-call cap is a calculator support boundary, not an official pricing threshold.

Try the illustrative workload, which is explicitly **not live task usage**:

```text
python plugins/codex-orchestrator/scripts/cost_receipt.py plugins/codex-orchestrator/examples/illustrative-usage.json
```

The calculator emits JSON and supports `--pricing PATH`. The
[operations reference](plugins/codex-orchestrator/skills/orchestration/references/operations.md)
documents its strict input contract and receipt limitations.

## Development and verification

From a checkout:

```text
python plugins/codex-orchestrator/scripts/verify.py
```

The same portable entry point runs in CI on Ubuntu, Windows, and macOS with Python
3.12, plus Python 3.11 on Ubuntu for the minimum version. It validates packaging,
links, attribution, policy contracts, and tests. The POSIX `verify.sh` is only a
convenience wrapper. Scripts resolve bundled resources from their own location.

Tests cover accounting, capability/effort checks, mode concurrency, risk routing,
independent work, invalid inputs, package integrity, and portable paths. The
[offline routing helper](plugins/codex-orchestrator/scripts/routing_policy.py) applies
Astra-supplied classifications; it does not discover capabilities or dispatch agents.
These tests cannot prove natural-language classification quality or live model pins.
See [CONTRIBUTING.md](CONTRIBUTING.md) for host smoke checks and upstream maintenance,
and [CHANGELOG.md](CHANGELOG.md) for the fork transition.

## Acknowledgements and license

- [DannyMac180/astra-advisor](https://github.com/DannyMac180/astra-advisor) is the
  primary upstream and fork foundation: Astra orchestration authority, dynamic
  capability delegation, native explicit controls, preflight/runtime evidence,
  fail-closed behavior, fresh review, parent verification/acceptance, and cost receipts.
- [DannyMac180/sol-advisor](https://github.com/DannyMac180/sol-advisor) inspired
  capability lanes, Luna / Max for bounded implementation, Terra for engineering
  judgment, bounded contracts, selective delegation, fresh review, and parent acceptance.
- [donvito/codex-astra-luna-orchestrator](https://github.com/donvito/codex-astra-luna-orchestrator)
  inspired Astra as root, cheaper specialized workers, clear roles, bounded ownership,
  concise returned evidence, and moving large mechanical workloads out of parent context.
- [addyosmani/agent-skills](https://github.com/addyosmani/agent-skills) inspired
  structured specification, planning, implementation, debugging, testing, verification,
  review, and shipping workflows, with optional interoperability.

These relationships do not imply endorsement. This fork retains upstream code and
its MIT notice; the other projects are conceptual inspiration, with no source code
or skill collections copied into the plugin. The original copyright and permission
notice are preserved in [LICENSE](LICENSE) and the
[installed package license](plugins/codex-orchestrator/LICENSE). Keep that notice with redistributed
copies or substantial portions of the software.
