# Revision 0969 changelog

## Repeated search product repair

- Made `findnext` wrap from the final match to the first with explicit
  `[wrapped to top]` feedback.
- Made `findprev` wrap from the first match to the final with explicit
  `[wrapped to bottom]` feedback.
- Made initial `find` wrap when the cursor is after the final match.
- Made a sole match return false with `[only match]` instead of reporting a
  cursor-stationary success.
- Replaced cursor-column increment/clamp progression with flat source-offset
  ordering, fixing newline-starting match rediscovery.

## Shared source-coordinate semantics

- Consolidated literal and regex search into one ordered set of non-empty,
  non-overlapping spans in original buffer coordinates.
- Preserved ignore-case source offsets by escaping literal queries and applying
  `re.IGNORECASE` without lower/casefold copies.
- Made zero-width regex omission consistent across navigation, `i/n` status, and
  visible highlighting.
- Reused the exact resolved match index/count in navigation messages rather than
  rescanning after cursor mutation.

## Viewport and performance refactor

- Removed the editor-local row-fragment match implementation.
- Projected whole-buffer matches into visible source fragments, preserving
  cross-line matches and preventing softwrap/horizontal-scroll fragments from
  inventing regex anchors.
- Added one transient exact-buffer/version/query/options snapshot shared by
  status and highlights during composed screen assembly.
- Rejected snapshots from another same-version buffer and after mutation.
- Added monotonic span start/end indexes and bisected viewport projection.
- Removed trailing-tuple slicing so a visible row does not copy every remaining
  match after its bisected start.
- Added no option, registry, pane, schema, background worker, indexer, or
  persistent cache.

## Evidence and documentation

- Added 13 focused repeated-search journeys covering wrap, no-op truth,
  newline/overlap/Unicode/zero-width semantics, cross-line projection,
  softwrap/hscroll anchors, snapshot identity, and one-scan screen composition.
- Updated the mission, roadmap, repo map, worklist, host API, editor behavior,
  research, decision, and revision-index surfaces.
- Added `docs/925-search-wrap-source-match-viewport-projection.md` with the
  transcript, severe failure analysis, primary-source research, refactor,
  residual risks, and next speculation.
