# Rev662 / rev721 — replace zero-width hygiene

Rev721 is a small bulk-edit trust cleanup for ordinary `replace` and
`replaceall`. The adjacent `qreplace` path already learned in rev719 to reject
empty searches and zero-width regex matches before entering capture mode, and
rev720 made the whole replace family reject unknown flags before guessing at a
user's intent. One ordinary replace seam still stayed too permissive: the
non-interactive commands could still accept a search that did not describe a
visible, advancing span.

The dangerous cases are small but surprising:

- `replace '' X -l` can behave like an invisible insertion point rather than a
  visible text replacement.
- `replace '' X -a -l` and `replaceall '' X -l` can insert around every
  character because Python's empty-string replacement semantics are defined at
  every boundary.
- `replace '$' X` can edit at an invisible end anchor.
- `replace '$' X -a` and `replaceall '$' X` can bulk-edit an invisible anchor.
- `replaceall 'abc|$' X` can partially replace `abc` and still also match the
  zero-width end anchor later.

The fix keeps successful replacement behavior unchanged for normal searches:

- empty searches fail early with `replace: empty search` or
  `replaceall: empty search`;
- single regex `replace` checks the first match before editing and rejects it if
  `start == end`;
- bulk regex `replace` / `replaceall` preflight every match for zero width before
  calling `subn`, so an eventually-zero-width pattern cannot leave a partial
  edit behind;
- all failures preserve the current buffer text and keep the command family in
  the message, for example `replaceall: zero-width matches are not supported`.

This deliberately does not add new replacement syntax or change regex template
expansion. It only aligns ordinary replacement with the trust rule that query
replace already made explicit: editing commands should operate on visible,
advancing matches, and they should stop before mutating when the search target is
invisible.

## Focused tests

- `tests/test_editor_core.py`
