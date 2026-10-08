# Micromax revision 0967

## Outcome

Rev0967 makes the editor's existing selection and syntax truth visible through
one bounded model consumed by both the compact headless contract and the
reference curses TUI. Primary and secondary selections, including selected
logical newlines, can no longer remain active while looking like ordinary text.

## Product repair

- Projected Micromax syntax spans and multicursor selections onto horizontal and
  soft-wrapped viewport fragments.
- Painted primary and secondary selections with canonical emphasis, so lower
  syntax/diagnostic attributes cannot make them collide with the current search
  match inside the primary range.
- Represented a selected logical newline as one visible blank-cell cue, including
  newline-only and empty-line selections.
- Added one strict 80x24 edit -> help -> command-palette/status journey through
  the public compact screen contract.
- Updated the query-replace golden journey so its active match must now be
  visibly selected.

## Bounded shared model

- Retained the primary while considering at most 4096 cursor sources per screen
  snapshot; reported omitted sources and counted only selections that actually
  intersect the viewport as visible.
- Scanned each visible Micromax logical line once from column zero through the
  furthest visible source column, capped at 4096 characters; truncated remainder
  stays plain and is reported.
- Kept `micromax.screen.v1`'s closed object shape and added compatible
  `syntax-*`, `selection-secondary`, and `selection-primary` cue values.
- Declared and tested one finite low-to-high highlight precedence instead of
  relying on renderer call order.

## Audit/refactor

- Added an exact `source_text_x` / `source_text_length` seam to wrapped rows so
  renderer-owned continuation indentation is never mistaken for file text.
- Moved live trailing-whitespace, tab-error, brace, and color-column geometry out
  of the curses paint loop; the renderer consumes shared cue rows.
- Removed repeated whole-cursor normalization from selection-heavy reads.
- Reused one normalized status snapshot for infobar and statusline composition.
- Fixed prompt cursor placement after horizontal editing scroll by consuming the
  composed screen cursor instead of rereading status and subtracting edit scroll.
- Kept the generated handoff bounded at 64 documents by prioritizing core and
  recent-revision evidence, then using older stable docs only to fill remaining
  slots.

## Honest boundary

Coordinates remain Python code points rather than terminal cells or grapheme
clusters. Syntax is Micromax-only and line-local. Secondary selections are
unioned per row, terminal styling varies, and screen projection is bounded only
after application-owned cursor normalization. No complete repository-suite claim
is made.
