# Contributing to codex-orchestrator

Keep this a focused native Codex orchestration plugin. Favor a small, inspectable
policy change over custom runtime machinery. Explain the concrete task that needs
the change, expected behavior, and verification evidence in an issue or pull request.

## Local development

Use Git and Python 3.11+ (3.12 recommended) on Windows, Linux, or macOS. No Python
packages or external skill collections need installing. From a checkout, run:

```text
python plugins/codex-orchestrator/scripts/verify.py
```

Use your platform's Python launcher if it differs. The entry point validates the
package and runs all tests, including the preserved cost-receipt suite. CI uses
Python 3.12 on all three operating systems and 3.11 on Ubuntu. Keep paths relative
to the script/package with `pathlib`; invoke subprocesses as argument lists with
`sys.executable` and no `shell=True`. Shell wrappers must remain optional.

## Boundaries and changes

- [SKILL.md](plugins/codex-orchestrator/skills/orchestration/SKILL.md) is the entry
  policy loaded by Codex; keep it concise enough to use on every task.
- [routing-policy.md](plugins/codex-orchestrator/skills/orchestration/references/routing-policy.md)
  owns mode behavior, capability classification, delegation contracts, optional
  workflows, and reviewer policy.
- [operations.md](plugins/codex-orchestrator/skills/orchestration/references/operations.md)
  owns native preflight, realized-setting evidence, lifecycle, and accounting rules.
- [routing_policy.py](plugins/codex-orchestrator/scripts/routing_policy.py) is a
  small offline check of an explicit classification. It is not an automatic router
  or enforcement layer around Codex. Change fixtures/tests together with policy.
- [cost_receipt.py](plugins/codex-orchestrator/scripts/cost_receipt.py) retains the
  upstream strict accounting contract. Do not weaken its unknown-usage or coverage
  safeguards to manufacture savings.

Test behavior and negative cases, not merely implementation wording. Policy anchor
checks prevent accidental removal of critical instructions but cannot establish
semantic compliance. Review the full prose and fixtures for contradictions as well.
No test can prove a model's first-attempt success from a task-class label. Record
new evidence when a classification fails and reassess the boundary; do not build
automatic retries or train a speculative router.

Before submitting, run verification, inspect the complete diff, and obtain a fresh
read-only review appropriate to the change's risk. Record checks, assumptions,
runtime limitations, and residual risks. The integrating maintainer owns acceptance.
Update README/operations/examples for public behavior changes and add a concise
changelog entry. Do not add another public mode without revisiting the two-mode design.

## Native host smoke check

Offline tests do not prove plugin installation, live routing, or realized settings.
For a release, record the host/version and perform these checks in a disposable
project with the required native controls:

1. Install this checkout as a local marketplace using the README commands; start a
   fresh GPT-6 Astra task and invoke the plugin without external engineering skills.
2. In each mode, request a useful bounded discovery task. Confirm the route reports
   the mode, ownership, selection reason, explicit Luna maximum effort, and fresh
   context. Observe realized settings when exposed; otherwise record unconfirmed.
3. Request bounded judgment work and verify direct Terra selection is possible
   without a failed Luna attempt. Use a genuinely difficult case to inspect Sol's
   justification. Do not force extra delegates merely to fill the mode cap.
4. Verify trivial work can stay solo and normal-risk implementation receives a
   fresh Terra review followed by parent verification/acceptance. Check behavior
   at the cap and rejection of duplicate work.
5. On a host lacking required controls, verify delegation reports the limitation
   and does not substitute a model or launch another inference mechanism. If a
   realized route mismatches, stop the affected work and withhold acceptance.
6. Confirm receipts separate estimates from actual quota and missing telemetry
   stays unavailable. Do not use the illustrative fixture as task evidence.

Report these separately from automated CI results; do not claim a host smoke check
was performed merely because the unit tests passed. Account/model availability is
controlled by the host and cannot be provided by this plugin.

## Upstream and licensing

The fork foundation is [DannyMac180/astra-advisor](https://github.com/DannyMac180/astra-advisor).
Its MIT license and Daniel McAteer copyright remain in [LICENSE](LICENSE), with an
identical [package copy](plugins/codex-orchestrator/LICENSE) for installed distributions.
The other acknowledged projects supplied conceptual inspiration, not copied code.
Before importing any new source, inspect its license and preserve required notices.

The only directory move in this transition is `plugins/astra-advisor` to
`plugins/codex-orchestrator` for consistent public identity. Compare the corresponding
paths when reviewing upstream changes. Keep accounting and native lifecycle changes
separate from routing policy where practical; cherry-pick useful upstream safeguards
and adapt identity/policy conflicts explicitly. Avoid unrelated formatting churn.
Do not restore upstream newsletter tracking or personal installation assumptions as
package requirements. Acknowledgement does not imply endorsement.

Historical pricing snapshots are immutable evidence, not live prices. Add a new
dated snapshot with official sources when rates change and verify calculator
eligibility; never rewrite old receipts to use new prices.
