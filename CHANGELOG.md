# Changelog

## 0.4.0 — Unreleased

### Changed

- Simplify default routing around Astra + Luna: economy uses Luna Medium for mechanical work and Luna maximum-individual reasoning for bounded execution; balanced uses Luna maximum-individual plus Terra High for justified engineering judgment.
- Keep difficult/architectural work with the Astra parent by default; allow a fresh Astra Low delegate only when independent context/parallelism justifies the handoff.
- Remove Sol from default lanes. Sol remains an explicit user override for experiments, with a supported effort and reason.
- Treat Astra Low as a recommended parent starting point without mutating the user's selected parent effort.
- Split routing outcomes into `delegate`, `parent`, `wait`, `skip`, and `blocked`; capacity/dependency waits no longer imply parent execution.
- Separate delegability from concurrency safety, honor lower host limits, and exclude topology-changing Ultra from Luna's default maximum-individual policy.
- Route fresh review by both mode and risk: economy uses Astra Low for normal/high risk; balanced uses Terra High for normal and Astra Low for high risk. Exceptional risk always requires an explicit Astra decision.
- Reduce mandatory orchestration context. Accounting is removed from the installed plugin and preserved under repository-root `tools/accounting/` for optional historical/manual use.
- Keep lifecycle reporting compact and make client/version-specific host smoke checks explicit.

### Added

- `task_state.py`, an advisory declared-state validator for dependencies, one-writer ownership, capacity, requested/observed settings, budgets, review freshness and current-revision acceptance.
- Pre-dispatch dispatch/correction/review budgets as reassessment gates, never correctness waivers.
- Optional evaluation guidance for repeatable root-only/economy/balanced experiments without claiming API-dollar estimates are subscription quota.

### Migration

- Start a fresh task after upgrading so the 0.4 routing policy is loaded.
- If you depended on the installed `cost_receipt.py`, use `tools/accounting/scripts/cost_receipt.py` manually instead; accounting is no longer a runtime plugin feature.
- Existing explicit Sol experiments must now be expressed as user overrides rather than relying on a default difficult-work lane.

## 0.3.0

- Evolved the Astra Advisor fork into `codex-orchestrator` with economy/balanced routing, native runtime-evidence safeguards, optional engineering workflows, fresh review and historical API-equivalent accounting.
