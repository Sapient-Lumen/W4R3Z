# Archived README through rev0951

Preserved before the rev0952 living-document compaction.

---

Rev0951 note: mxtimely summaries now distinguish partial prefixes from completed lanes, and mxaudit hard-checks completion-honest summary evidence.

Latest tiny landing (rev0951): `tools/mxtimely.py` writes v3 summary JSON with `status`, `complete`, `planned_steps`, and `pending_steps`; interrupted cloudtainer prefixes now leave `ok: false` / `status: partial` instead of a success claim. `tests/test_mxtimely.py` pins the completed and interrupted cases, `mxaudit --check` reports `timely_summary_completion_honest`, and the old TODO trail is archived at `docs/history/TODO-through-rev0950.md` to keep the live handoff small.

# Micromax

Micromax is a small concatenative language, a reference Python VM, and a
headless-plus-curses editor host for **capability-scoped end-user automation**.
The language is the editor's configuration, macro, and plugin substrate; the
editor is the first proving ground for a reusable least-authority host.

## What matters most

- Small, portable language semantics with a Python reference oracle.
- Explicit host effects and capability checks instead of ambient authority.
- Provenance, rollback, and recoverable failure around extension behavior.
- Stable headless models that can be tested without a terminal UI.
- A calm editor judged by taste, trust, and flow.

Micromax is experimental. Its current capability system is an application-level,
in-process boundary—not an operating-system sandbox for malicious plugins.
Instruction budgets, origin checks, filesystem roots, restricted startup,
cleanup commit guards, retained cleanup diagnostics, opt-in durable cleanup
failure receipts, scoped live-callback rollback, and touched command/action/keymap/timer/hook/mark/delayed-row/
singleton-help/recovery/interaction group rollback plus generation-scoped
macro, non-macro, delayed-interaction, recent-files owner, palette-recent owner, active-search owner, prompt-history owner, saved-cursor owner, help-history owner, recovery owner, option-state owner, and mark owner rollback are useful guardrails, but they do not bound all
memory, blocking calls, native code, or process compromise. See `docs/00-vision.md`,
`docs/security-boundaries.md`,
`docs/831-cloudtainer-mission-effect-lifecycle-audit.md`,
`docs/832-observable-cleanup-live-option-rollback.md`,
`docs/833-runtime-cleanup-commit-guards.md`,
`docs/834-narrow-runtime-group-snapshot.md`,
`docs/835-runtime-generation-cleanup-guard.md`,
`docs/836-plugin-cleanup-diagnostics.md`,
`docs/837-command-group-journal-feedback.md`,
`docs/838-action-keymap-timer-group-snapshots.md`,
`docs/839-hook-mark-group-snapshots.md`,
`docs/840-delayed-state-group-snapshots.md`,
`docs/841-singleton-help-group-snapshots.md`,
`docs/842-recovery-interaction-group-snapshots.md`,
`docs/843-generation-row-snapshots.md`,
`docs/844-macro-generation-snapshots.md`,
`docs/845-plugin-cleanup-durable-log.md`,
`docs/846-plugin-callback-scoped-rollback.md`,
`docs/847-cloudtainer-heart-gap-waste-word-authority.md`,
`docs/848-retired-wordlist-tombstones-package-budgets.md`,
`docs/849-retired-deferred-callback-guard.md`,
`docs/850-generation-interaction-cleanup.md`,
`docs/851-stale-macro-timer-budget.md`,
`docs/852-cloudtainer-timely-tool-runway.md`,
`docs/853-timely-full-suite-release.md`,
`docs/854-testing-runway-ux.md`,
`docs/855-cloudtainer-process-tree-timeout-audit.md`,
`docs/856-hostcall-result-budget.md`,
`docs/857-regex-hostcall-input-preflight.md`,
`docs/858-regex-timeout-worker.md`,
`docs/859-structured-model-dimension-budget.md`,
`docs/860-fs-read-preflight-budget.md`,
`docs/861-query-input-budget.md`,
`docs/862-scan-row-budget.md`,
`docs/863-source-load-eval-budget.md`,
`docs/864-source-load-graph-budget.md`,
`docs/865-path-completion-scan-budget.md`,
`docs/866-shell-output-timeout-budget.md`,
`docs/867-external-clipboard-process-budget.md`,
`docs/868-fs-stat-timeout-worker.md`,
`docs/869-fs-list-timeout-worker.md`,
`docs/870-cloudtainer-heart-mission-fs-read-timeout.md`,
`docs/871-open-prompt-filesystem-timeout.md`,
`docs/872-atomic-write-timeout.md`,
`docs/873-save-preflight-timeout.md`,
`docs/874-diskstate-status-cache.md`,
`docs/875-status-slow-refresh.md`,
`docs/876-palette-stat-batch.md`,
`docs/877-status-access-bounded.md`,
`docs/878-plugin-discovery-fingerprint-timeout.md`,
`docs/879-docs-catalog-scan-timeout.md`,
`docs/880-project-root-marker-batch.md`,
`docs/881-help-doc-read-timeout.md`,
`docs/882-cloudtainer-heart-mission-waste-audit.md`,
`docs/883-plugin-meta-contained-existence.md`,
`docs/884-prompt-completion-contained-provenance.md`,
`docs/885-stdlib-resource-contract.md`,
`docs/886-timer-owner-cancel-release.md`,
`docs/887-archive-provenance-verifier.md`,
`docs/888-package-input-policy.md`,
`docs/889-qreplace-all-budget.md`,
`docs/890-pending-open-url-owner.md`,
`docs/891-qreplace-owner-snapshot.md`,
`docs/892-prompt-owner-snapshot.md`,
`docs/893-keymode-owner-snapshot.md`,
`docs/894-plugin-callback-interaction-owner.md`,
`docs/895-clipboard-owner-snapshot.md`,
`docs/896-macro-owner-generation-snapshot.md`,
`docs/897-cloudtainer-entrypoint-freshness-audit.md`,
`docs/33-effect-resource-contract.md`,
`docs/898-generated-effect-resource-contract.md`,
`docs/899-active-search-owner-contract.md`,
`docs/900-prompt-history-owner-contract.md`,
`docs/901-recent-files-owner-contract.md`,
`docs/902-saved-cursor-owner-contract.md`,
`docs/903-palette-recent-owner-contract.md`,
`docs/904-help-history-owner-contract.md`,
`docs/905-recovery-owner-contract.md`,
`docs/906-effect-contract-installed-help.md`,
`docs/908-mark-owner-contract.md`,
`docs/907-option-state-owner-contract.md`, and
`docs/909-timely-summary-completion-honesty.md`. The full narrow-change trail remains
in `docs/revision-index.json`.

## Try it

Language REPL:

```bash
python -m micromax.repl
```

Headless editor and docs rendering:

```bash
python -m micromax_editor
python -m micromax_editor path/to/file.txt
python -m micromax_editor --help-doc 00-vision --dump-screen 24 80
python -m micromax_editor --trust restricted path/to/file.txt
```

Curses UI:

```bash
python -m micromax_editor --tui
python -m micromax_editor --tui path/to/file.txt
```

## Development

```bash
make bootstrap
make timely
make timely-tests
make release-suite
make release-verify
make test
make doctor
python tools/mxlint.py
python tools/mxcontext.py --check
make audit-metrics
make effect-contracts
```

Runtime or tooling changes invalidate prior release evidence. The short-window
full-suite lane checkpoints selected file batches and only `make release-verify` makes a
full-release claim:

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src make release-suite
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src make release-verify
```

The older node/chunk aggregate lane remains available when whole-suite pytest
collection fits the host:

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src make test-all-chunks
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src make test-verify-current
```

`tools/mxcontext.py` is intentionally curated. It lists durable entrypoints and
the newest revision notes, reports full-corpus counts, and points to
`docs/revision-index.json` instead of reproducing that catalog.

## Read in this order

1. `docs/00-vision.md` — mission, security truth, and non-goals.
1. `docs/security-boundaries.md` — concrete actors, assets, mitigations, and residual risks.
1. `docs/909-timely-summary-completion-honesty.md` — current cloudtainer landing: the heart/gap/waste read is recorded and mxtimely summary evidence now distinguishes completed lanes from partial prefixes.
1. `docs/908-mark-owner-contract.md` — prior runtime/audit landing: named mark rollback routes through public editor-owned mark methods, the generated contract exposes `ed.mark-register`, and redundant recent-files group restore was removed.
1. `docs/907-option-state-owner-contract.md` — prior runtime/audit landing: failed source/lifecycle and scoped callback option rollback route through public editor-owned option methods and the generated contract exposes `ed.option-state-register`.
1. `docs/906-effect-contract-installed-help.md` — prior installed-surface landing: the generated effect/resource contract renders into installed help and audit checks its freshness.
1. `docs/905-recovery-owner-contract.md` — prior runtime/audit landing: selection-stack and jump-list recovery rows route through editor-owned owner methods and the generated contract exposes `ed.recovery-register`.
1. `docs/904-help-history-owner-contract.md` — prior runtime/audit landing: help-history group/generation/broad rollback routes through editor-owned owner methods and the generated contract exposes `ed.help-history-register`.
1. `docs/903-palette-recent-owner-contract.md` — prior runtime/audit landing: command-palette recent rollback routes through editor-owned owner methods and the generated contract exposes `ed.palette-recent-register`.
1. `docs/902-saved-cursor-owner-contract.md` — prior runtime/audit landing: saved-cursor path+position rollback routes through editor-owned owner methods and the generated contract exposes `ed.saved-cursor-register`.
1. `docs/901-recent-files-owner-contract.md` — prior runtime/audit landing: recent-files group/generation/broad rollback routes through editor-owned owner methods and the generated contract exposes `ed.recent-files-register`.
1. `docs/900-prompt-history-owner-contract.md` — prior runtime/audit landing: prompt-history group/generation/broad rollback routes through editor-owned owner methods and the generated contract exposes `ed.prompt-history-register`.
1. `docs/899-active-search-owner-contract.md` — prior runtime/audit landing: active-search group/generation/broad rollback routes through editor-owned owner methods and the generated contract exposes `ed.active-search-register`.
1. `docs/898-generated-effect-resource-contract.md` — prior runtime/audit landing: high-risk host-effect/resource rows are generated from live registries, capability policy, defaults, stdlib contract, regex defaults, and audit evidence.
1. `docs/897-cloudtainer-entrypoint-freshness-audit.md` — prior cloudtainer audit: heart/gap/waste diagnosis and curated-entrypoint freshness invariant.
1. `docs/896-macro-owner-generation-snapshot.md` — prior runtime/audit landing: generation-scoped saved macro/live recording rollback routes through editor-owned owner methods.
1. `docs/895-clipboard-owner-snapshot.md` — prior runtime/audit landing: clipboard group/generation and broad registration rollback route through editor-owned owner methods.
1. `docs/894-plugin-callback-interaction-owner.md` — prior runtime/audit landing: broad failed-callback interaction snapshot/restore routes through one editor-owned aggregate owner.
1. `docs/893-keymode-owner-snapshot.md` — prior runtime/audit landing: keymode group/generation snapshot/restore routes through editor-owned owner methods.
1. `docs/892-prompt-owner-snapshot.md` — prior runtime/audit landing: prompt group/generation snapshot/restore routes through editor-owned owner methods.
1. `docs/891-qreplace-owner-snapshot.md` — prior runtime/audit landing: query-replace group/generation snapshot/restore routes through editor-owned owner methods with coupled session+cursor state.
1. `docs/890-pending-open-url-owner.md` — prior active-interaction owner landing: pending external-URL confirmation snapshot/restore uses editor-owned group/generation methods.
1. `docs/889-qreplace-all-budget.md` — prior runtime/audit landing: `qreplace all` has a host-owned per-action replacement budget, visible recovery behavior, and audit coverage.
1. `docs/888-package-input-policy.md` — prior release-hygiene landing: package/dependency inputs have an executable no-runtime-deps/no-lock policy report, audit check, and archive-embedded handoff row.
1. `docs/887-archive-provenance-verifier.md` — prior release-hygiene landing: revision zips verify embedded archive-member provenance, unsafe/duplicate members, and verifier resource budgets.
1. `docs/886-timer-owner-cancel-release.md` — prior runtime/audit landing: canceled timers release live callback rows immediately, stale heap ids are bounded, and plugin-runtime timer rollback goes through the timer owner seam.
1. `docs/885-stdlib-resource-contract.md` — prior runtime/audit landing: bundled stdlib startup is explicit package-resource I/O with a byte ceiling, SHA-256 provenance, health rows, and audit coverage.
1. `docs/884-prompt-completion-contained-provenance.md` — prior runtime/tooling landing: prompt path completion uses contained directory listing for standalone and editor paths, and revision zips embed archive-member SHA-256 provenance.
1. `docs/883-plugin-meta-contained-existence.md` — prior runtime/audit landing: optional plugin metadata existence uses contained plugin I/O, escaping metadata fails closed, docs-index fallback reads are contained, and timely evidence is incremental.
1. `docs/882-cloudtainer-heart-mission-waste-audit.md` — prior cloudtainer audit: mission, missing contracts, waste, next code repair, and online research.
1. `docs/881-help-doc-read-timeout.md` — prior runtime/editor landing: help-doc open/read, explicit docs path resolution, relative help-link following, and target-heading metadata use bounded contained filesystem seams.
1. `docs/880-project-root-marker-batch.md` — prior runtime/editor landing: recent/buffer project-root grouping batches parent-marker stat work through a bounded filesystem worker and short-lived cache.
1. `docs/879-docs-catalog-scan-timeout.md` — prior runtime/editor landing: docs/help catalog scanning uses a bounded killable top-level inventory with row, byte-prefix, total-byte, and wall-clock budgets.
1. `docs/878-plugin-discovery-fingerprint-timeout.md` — prior runtime/editor landing: plugin discovery uses bounded contained top-level listing and restricted manual-load package fingerprinting runs in a killable worker.
1. `docs/877-status-access-bounded.md` — prior runtime/editor landing: parsecursor literal-path checks and status read-only refresh use bounded filesystem observation instead of direct stat/access probes.
1. `docs/876-palette-stat-batch.md` — prior runtime/editor landing: command-palette recent/known-path disk truth batches visible stat work through one bounded filesystem worker and one-build cache.
1. `docs/875-status-slow-refresh.md` — prior runtime/editor landing: hot status disk/read-only observation uses seeded cache rows plus a stale-marked slow-refresh cadence, while explicit recovery/save paths force live bounded checks.
1. `docs/874-diskstate-status-cache.md` — prior runtime/editor landing: hot status/disk-state rendering uses a short explicit cache while live diskstate rows/hostcalls and save/prompt preflights keep bounded exact checks.
1. `docs/873-save-preflight-timeout.md` — prior runtime/editor landing: save preflight directory-kind, freshness/hash, and mkparents work have bounded seams before the atomic writer starts.
1. `docs/872-atomic-write-timeout.md` — prior runtime/editor landing: atomic save and persistence writes use a VM-tunable killable worker with temp cleanup.
1. `docs/871-open-prompt-filesystem-timeout.md` — prior runtime/editor landing: command open/revert/source/user-init reads plus prompt/palette path completion use bounded filesystem timeout seams.
1. `docs/870-cloudtainer-heart-mission-fs-read-timeout.md` — prior cloudtainer audit/runtime landing: mission/gap/waste diagnosis plus `ed.fs-read` timeout-worker repair.
1. `docs/869-fs-list-timeout-worker.md` — prior runtime/editor landing: `ed.fs-list` uses a VM-tunable killable worker timeout around fd-bound directory traversal.
1. `docs/868-fs-stat-timeout-worker.md` — prior runtime/editor landing: `ed.fs-stat` uses a VM-tunable killable worker timeout around fd-bound metadata observation.
1. `docs/867-external-clipboard-process-budget.md` — prior runtime/editor landing: bounded external clipboard helper input/output and timeout/process-tree teardown.
1. `docs/866-shell-output-timeout-budget.md` — prior runtime/editor landing: bounded `ed.shell` command input, output capture, and timeout/process-tree teardown.
1. `docs/865-path-completion-scan-budget.md` — prior runtime/editor landing: command-prompt filesystem completion uses the shared scan budget before directory iteration/sort.
1. `docs/864-source-load-graph-budget.md` — prior runtime/editor landing: VM-tunable source dependency-depth and cumulative-byte budgets.
1. `docs/863-source-load-eval-budget.md` — prior runtime/editor landing: VM-tunable source-size and eval-step budgets for executable source loads.
1. `docs/862-scan-row-budget.md` — prior runtime/editor landing: VM-tunable scan/row budgets for broad picker and filesystem-list hostcalls.
1. `docs/861-query-input-budget.md` — prior runtime/editor landing: free-text query byte preflight for broad scan/prompt hostcalls.
1. `docs/860-fs-read-preflight-budget.md` — prior runtime/editor landing: pre-read byte budget for `ed.fs-read` with final read recheck.
1. `docs/859-structured-model-dimension-budget.md` — prior runtime/editor landing: preflight dimensions for structured screen/docs/help/prompt model hostcalls.
1. `docs/858-regex-timeout-worker.md` — prior runtime landing: subprocess containment for risky regex hostcalls.
1. `docs/857-regex-hostcall-input-preflight.md` — regex hostcall input preflight and argument-preserving boundary failures.
1. `docs/856-hostcall-result-budget.md` — shared VM-visible hostcall result budgets and the next resource-exhaustion path.
1. `docs/855-cloudtainer-process-tree-timeout-audit.md` — prior deep audit: mission, missing contract, waste, online research, and escaped process-tree timeout repair.
1. `docs/853-timely-full-suite-release.md` — tooling landing: resumable per-file full-suite release evidence for short sessions.
1. `docs/852-cloudtainer-timely-tool-runway.md` — prior tooling landing: bounded Python handoff checks for short cloudtainer sessions.
1. `docs/851-stale-macro-timer-budget.md` — prior runtime landing: stale saved macro slots are pruned before playback and `ed.after` has a pending-work budget.
1. `docs/850-generation-interaction-cleanup.md` — active prompt/qreplace/open-url/keymode rows clean up by plugin generation.
1. `docs/849-retired-deferred-callback-guard.md` — stale plugin keybinding/hook/timer callbacks from retired generations are refused before execution.
1. `docs/848-retired-wordlist-tombstones-package-budgets.md` — old plugin wordlists become compact tombstones and package fingerprinting has budgets.
1. `docs/847-cloudtainer-heart-gap-waste-word-authority.md` — mission/gap/waste audit, fixed provenance leak, retained-wordlist finding, research, and sequencing.
1. `docs/831-cloudtainer-mission-effect-lifecycle-audit.md` — earlier deep diagnosis and effect-contract baseline.
1. `docs/832-observable-cleanup-live-option-rollback.md` — cleanup evidence and live-buffer option rollback.
1. `docs/833-runtime-cleanup-commit-guards.md` — fail closed on cleanup/retag commit failures.
1. `docs/834-narrow-runtime-group-snapshot.md` — rollback only group-sweep surfaces for cleanup/retag guards.
1. `docs/835-runtime-generation-cleanup-guard.md` — guarded generation-scoped delayed-state cleanup.
1. `docs/836-plugin-cleanup-diagnostics.md` — retained cleanup reports are user/headless visible.
1. `docs/846-plugin-callback-scoped-rollback.md` — live plugin callback rollback is group/generation scoped.
1. `docs/845-plugin-cleanup-durable-log.md` — cleanup failure receipts can be persisted behind `cap.persist`.
1. `docs/844-macro-generation-snapshots.md` — macro generation cleanup is plugin-root/generation scoped.
1. `docs/843-generation-row-snapshots.md` — non-macro generation cleanup is plugin-root/generation scoped.
## Handoff archives

```bash
make revzip TAG=foobarnamesummaryhighlightcodename
make revzip-verify ZIP=Micromax-rev####-stamp-tag.zip
```

Each linked session artifact should preserve the filename contract:

```text
Project-Name-rev####-YYYY.MM.DD.HH.MM-foobarnamesummaryhighlightcodename.zip
```
