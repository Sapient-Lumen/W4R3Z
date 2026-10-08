# Revision 0972 changelog

## Plugin execution

- Made `plugin.json requires` the executable readable import graph rather than load-order metadata alone.
- Gave source, `preinit`, `init`, `postinit`, `deinit`, commands, bindings, timers, hooks, and other retained callbacks the same exact search order: self, direct dependencies in manifest order, transitive dependencies breadth-first, then Forth.
- Kept direct imports ahead of transitive implementation words while preserving late-bound dependency implementation calls.
- Removed ambient loaded siblings from plugin lookup and hook inventory.
- Kept only the executing plugin's wordlist writable and refused reachable module/wordlist creation during explicit plugin execution.

## VM ownership and mutation

- Added an embedding-owned `WordlistAccessScope` that leaves standalone VM behavior open by default.
- Preflighted wordlist inspection, search-order changes, `use`, `in`, `definitions`, module operations, and current-wordlist changes under an active scope.
- Made `VM._add_word()` the authoritative dictionary-write guard and stamped inserted words with their owning wordlist.
- Required owner-write authority for deferred behavior replacement through both `is` and `defer!`.
- Preserved stack operands on denied namespace/hostcall operations and restored the historical no-op behavior of `previous` on an empty order.
- Rejected partial namespace contexts and unknown scoped wordlist identifiers before mutating VM state; restored prior identity and scope after every context exit.

## Host extension surface

- Added a deliberately small executable plugin-surface classification: product-proven lifecycle/hostcalls are stable, unclassified calls are experimental, and exact host-owned presentation models are internal.
- Hid internal statusline, prompt, screen, gutter, edit-window, display, viewport, and bottom-row models from plugin `host.feature?` and `host.features`.
- Denied exact plugin-originated internal-model calls before consuming call evidence while preserving trusted headless/TUI access through the same bridge.
- Composed with any pre-existing host access policy and made installation idempotent.

## Audit, tests, and documentation

- Added focused regressions for undeclared imports, dependency writes, deferred rebinding, raw `set-current`, final mutation guarding, direct/transitive precedence, late-bound dependency code, hook disclosure, internal feature/call denial, delayed callbacks, and context rollback.
- Retained reload recovery by rewriting tests that previously relied on plugin-created ambient modules, which are now intentionally forbidden.
- Audited all bundled plugin direct hostcalls and pinned them to the stable set without cloning the full hostcall registry.
- Researched current VS Code, Component Model/WIT, Zed, and Wasmtime extension-boundary guidance from official sources.
- Updated living architecture, security, host API, plugin metadata, roadmap, worklist, and generated-context handoff documentation.


## Specialized line edits

- Added immutable move, duplicate, and delete-line plans that derive output lines and cursor/anchor projection from one pre-edit source snapshot.
- Preserved the semantic role of half-open whole-line trailing endpoints separately from ordinary cursors at the same `(line, 0)` coordinate.
- Fixed forward/reverse selection continuation through `MoveLinesUp` and `MoveLinesDown`, including ordinary cursors on the displaced neighboring line.
- Made `DuplicateLine` preserve primary column and source identity for secondary cursor/anchor state; selected blocks duplicate while the original directed selection remains selected.
- Reworked `CutLine` to cut every fully or partially selected source row, otherwise unique cursor rows, in ascending clipboard order and commit all deletions with one `touch_external()`, one exact dirty hash, and one undo boundary.
- Added pure-plan and editor-level regression tests, including exhaustive valid move spans/directions, cut-all normalization, edge no-ops, undo/redo exactness, and one-version multi-row cutting.

## Context curation

- Moved the oldest still-rooted recent evidence triplet (`REV0963_AUDIT.md`, `REV0963_CHANGELOG.md`, and `REV0963_TESTS.md`) into the established `docs/history/` lane and updated rev0963 lineage paths.
- Kept the generated context under its 64-document ceiling while retaining every historical body and adding the substantive rev0972 line-edit note.

## Mutation-point hardening and research

- Enforced plugin wordlist-creation authority inside `VM.new_wordlist()` so direct or future primitive callers cannot bypass source-level namespace preflight.
- Added a regression proving denied allocation leaves the next-wordlist counter, dictionaries, and names unchanged.
- Reviewed current Micro line-action source and a live move-lines continuation issue; recorded the narrow selection-boundary lesson without importing another editor architecture.
- Documented the measured removal of repeated dirty-hash work and the explicit limits around marks, diagnostics, folds, decorations, large files, and equal-text line identity.
