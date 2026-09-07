# Changelog

## 0.3.0 — Unreleased

### Changed

- Show API-equivalent receipts only with observed token usage or on explicit request;
  silently skip unavailable accounting by default while preserving the calculator.
- Route `fix-first` corrections by finding and capability instead of automatically
  assigning them to Astra; reassess repeated findings and preserve fresh review.
- Automatically select and apply relevant installed `agent-skills`, including
  delegate handoff; silently skip when unavailable without requesting installation.
- Evolve the Astra Advisor fork into `codex-orchestrator`, preserving MIT attribution,
  native delegation, runtime evidence safeguards, and API-equivalent accounting.
- Add exactly two public modes: recommended `balanced` (3 active delegates) and
  `economy` (2), with cheapest-capable classification before dispatch.
- Require Luna's maximum live-supported effort; default Terra/Sol to High for
  judgment/difficult work and choose fresh reviewers by risk.
- Make bounded ownership, new-information escalation, nonredundant delegation,
  optional installed workflows, and Astra final acceptance explicit.

### Added

- Offline routing checks with executable cases and negative tests, portable Python
  package verification, and Ubuntu/Windows/macOS CI with Python 3.11 minimum coverage.
- Public installation, contribution, host smoke-check, and upstream maintenance guidance.

### Migration

- Plugin/marketplace identity is now `codex-orchestrator`; install the new package
  and invoke `$codex-orchestrator:orchestration`. The plugin directory is now
  `plugins/codex-orchestrator`; update local script paths. Start a fresh task so the
  current policy loads, and avoid invoking the old and new orchestration skills together.
- Upstream 0.2.0 accounting input/output formats and its dated pricing snapshot remain
  compatible. Historical Astra Advisor attribution remains in the repository.
