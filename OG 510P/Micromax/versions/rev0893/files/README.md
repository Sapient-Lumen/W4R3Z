Rev0893 note: stale plugin macro playback now fails closed and ed.after has a host-owned pending timer budget.

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
macro, non-macro, and delayed-interaction rollback are useful guardrails, but they do not bound all
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
`docs/850-generation-interaction-cleanup.md`, and
`docs/851-stale-macro-timer-budget.md`. The full narrow-change trail remains
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
make test
make doctor
python tools/mxlint.py
python tools/mxcontext.py --check
make audit-metrics
```

Runtime changes invalidate prior aggregate evidence. Regenerate a resumable
aggregate manifest in cloudtainer-safe slices before making a full-release claim:

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src make test-all-chunks
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src make test-verify-current
```

`tools/mxcontext.py` is intentionally curated. It lists durable entrypoints and
the newest revision notes, reports full-corpus counts, and points to
`docs/revision-index.json` instead of reproducing that catalog.

## Read in this order

1. `docs/00-vision.md` — mission, security truth, and non-goals.
2. `docs/security-boundaries.md` — concrete actors, assets, mitigations, and residual risks.
3. `docs/851-stale-macro-timer-budget.md` — current runtime landing: stale saved macro slots are pruned before playback and `ed.after` has a pending-work budget.
4. `docs/850-generation-interaction-cleanup.md` — active prompt/qreplace/open-url/keymode rows clean up by plugin generation.
5. `docs/849-retired-deferred-callback-guard.md` — stale plugin keybinding/hook/timer callbacks from retired generations are refused before execution.
6. `docs/848-retired-wordlist-tombstones-package-budgets.md` — old plugin wordlists become compact tombstones and package fingerprinting has budgets.
7. `docs/847-cloudtainer-heart-gap-waste-word-authority.md` — mission/gap/waste audit, fixed provenance leak, retained-wordlist finding, research, and sequencing.
8. `docs/831-cloudtainer-mission-effect-lifecycle-audit.md` — earlier deep diagnosis and effect-contract baseline.
9. `docs/832-observable-cleanup-live-option-rollback.md` — cleanup evidence and live-buffer option rollback.
10. `docs/833-runtime-cleanup-commit-guards.md` — fail closed on cleanup/retag commit failures.
11. `docs/834-narrow-runtime-group-snapshot.md` — rollback only group-sweep surfaces for cleanup/retag guards.
12. `docs/835-runtime-generation-cleanup-guard.md` — guarded generation-scoped delayed-state cleanup.
13. `docs/836-plugin-cleanup-diagnostics.md` — retained cleanup reports are user/headless visible.
14. `docs/846-plugin-callback-scoped-rollback.md` — live plugin callback rollback is group/generation scoped.
15. `docs/845-plugin-cleanup-durable-log.md` — cleanup failure receipts can be persisted behind `cap.persist`.
16. `docs/844-macro-generation-snapshots.md` — macro generation cleanup is plugin-root/generation scoped.
17. `docs/843-generation-row-snapshots.md` — non-macro generation cleanup is plugin-root/generation scoped.
18. `docs/842-recovery-interaction-group-snapshots.md` — recovery stacks and delayed interactions are touched-group scoped.
19. `docs/841-singleton-help-group-snapshots.md` — clipboard/search/help-history rollback is touched-authority scoped.
20. `docs/840-delayed-state-group-snapshots.md` — delayed UI-state rows are touched-group scoped.
21. `docs/839-hook-mark-group-snapshots.md` — hook/mark cleanup rollback and mutable hook-handler clone fix.
22. `docs/838-action-keymap-timer-group-snapshots.md` — action/keymap/timer cleanup rollback is touched-group scoped.
23. `docs/837-command-group-journal-feedback.md` — command cleanup rollback and diagnostics hint baseline.
24. `TODO.md` — current revision and high-leverage next work.
25. `docs/830-plugin-option-rollback.md` — runtime option rollback boundary inherited from rev0872.
26. `docs/43-worklist.md` — active work lanes and stop conditions.
27. `docs/01-llm-start-here.md` — compact operational handoff.
28. `docs/02-repo-map.md` — architecture, structural risks, and evidence commands.
29. `docs/revision-index.json` — full structured revision history.

Historical living docs and the old vision preamble are under `docs/history/`.
Installed help is curated by `docs/installed-help-manifest.txt`.

## Handoff archives

```bash
make revzip TAG=foobarnamesummaryhighlightcodename
```

Each linked session artifact should preserve the filename contract:

```text
Project-Name-rev####-YYYY.MM.DD.HH.MM-foobarnamesummaryhighlightcodename.zip
```
