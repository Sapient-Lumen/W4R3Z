# Revision 0971 changelog

## Product

- Made empty buffer, recent-file, recent-directory, and project-file pickers prefer the most-recent useful *other* destination instead of selecting the already-active file.
- Made `Ctrl-O`, `Enter` toggle between the last two readable open project files without typing.
- Added a bounded `Open and recent` project section with explicit `active`, `previous`, `open`, `recent`, and dirty-combined cues.
- Kept typed project queries over the complete immutable scan rather than restricting search to the working-set prefix.
- Kept navigation pickers open when Enter cannot accept a target, preserving the exact query, selected row, project snapshot, script origin, and prompt keymode for correction or retry.
- Revalidated a selected recent-file row against the currently visible recent register before opening it, so a stale row cannot become raw path authority.

## Runtime and trust

- Kept the bounded filesystem scan as the sole project-path membership grant; MRU/recent state can only reorder or decorate exact snapshot members.
- Captured project context once under prompt-opening authority and deep-copied it with prompt lifecycle state.
- Replaced per-snapshot-member canonicalization with lexical in-memory comparison of only buffer/recent candidates, followed by exact inventory intersection.
- Read the authority-filtered recent register once when deriving preferred and avoided recent-picker targets.
- Preserved submit-time disappearance, regular-file, containment, symlink-swap, and delayed script-authority checks.
- Restored a failed navigation prompt only when the submission path did not deliberately install another prompt.

## Refactor and evidence

- Extracted deterministic project row planning and section labels to `micromax_editor.project_picker`, and normalized the captured inventory once per refresh rather than once for each context/status projection.
- Added a reusable prompt-layer initial-selection policy for preferred and avoided candidates.
- Extracted buffer-prompt submission from the main prompt dispatcher so success/failure lifecycle is shared across four navigation pickers.
- Added pure-model, repeated-toggle, MRU-return, stale-target, retry, dirty-state, immutable-snapshot, script-authority, status/TUI, and no-canonicalize-all-members regressions.
- Audited and corrected stale living documentation that still described foreground editor regex work and the already-completed navigation transcript as future work.
- Repaired `mxcontext`'s brittle exact-word handoff parser so the current `Latest substantive landing` label and historical `Latest tiny landing` labels share the same revision-mismatch and orphan detection.
- Restored the generated datacube budget by moving rev0961–rev0962 evidence triplets to `docs/history/` and removing two unchanged tests from rev0971's touched-code ledger; the compact handoff now resolves to 64 docs and 63 code paths.
