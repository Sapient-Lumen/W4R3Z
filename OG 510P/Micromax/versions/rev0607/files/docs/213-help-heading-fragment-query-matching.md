# Rev271 — docs heading queries can match heading fragment ids too

Rev271 extends the recent docs-heading query work one more tiny step: the
visible outline/help-nav row shape stays small (`[title kind menu info]`), but
heading queries now also reuse the heading's resolved fragment/id as hidden
ranking metadata.

That means:

- `helpjump custom-frag`
- `helpoutlinepick custom-frag`
- `helpnavpick custom-frag`

can all find `## Explicit fragment target {#custom-frag}` even though the raw id
stays out of the visible title row.

## Why this was the next honest move

Micromax already computes resolved heading fragments so docs links can follow
`#section` / `page.md#section`, and the shared docs-cues snapshot already
surfaces those fragments for future UIs/scripts/LLMs. The remaining gap was only
search: users could *follow* a stable anchor but could not *query* for it from
`helpjump` or the docs-heading pickers.

Current CommonMark still keeps headings lightweight rather than turning them into
a richer document tree, and Python-Markdown's current Attribute Lists docs still
teach explicit ids as a normal author-facing way to assign stable attributes to
markdown output. That keeps "fragment/id as hidden query metadata" squarely in
Micromax's tiny-source-truth style rather than pushing it toward a bigger docs
AST.

## Implementation shape

- added one tiny cached heading-line → fragment map for the current docs page
- `_help_outline_query_meta(row)` now appends the resolved fragment/id for the
  heading line when available
- visible rows stay unchanged; only ranking behavior changes
- `helpnavpick` inherits the behavior automatically because its heading half
  already starts from `help_outline_rows(query)`

## Coverage

Focused coverage lives in:

- `tests/test_editor_helpjump.py`
- `tests/test_editor_helpoutlinepick.py`
- `tests/test_editor_helpnavpick.py`
- `tests/test_mxcontext.py`
