# Rev433: exact current-doc heading detail row for `helpjump`

Before rev433, Micromax already had a good docs-heading navigation loop:

- `helpoutlinepick` / `helpnavpick` exposed searchable current-doc heading rows
- `helpjump QUERY` reused that same ranking logic for the best heading match
- query ranking already understood parent breadcrumbs and explicit heading fragments

But one tiny inspectability seam still lingered underneath that loop:

- `helpjump QUERY` still reparsed `help_outline_rows()` ad hoc inside the command layer
- scripts and future UIs had no named machine-facing sibling for the exact heading target they were about to jump to
- callers that wanted resolved fragment/section/position had to scrape picker rows or reimplement the same lookup logic

Rev433 keeps the change deliberately small:

- add `help_heading_detail_row(QUERY)` in the editor core
- expose it as hostcall `ed.help-heading-detail-row`
- make plain `helpjump QUERY` reuse that same shared row instead of reparsing outline text

The row shape is:

- `[topic title fragment level line col section]`

Where:

- `topic` is the current docs topic
- `title` is the resolved heading text
- `fragment` is the resolved explicit or auto heading fragment id
- `level` is the markdown heading level (`1..6`)
- `line` / `col` are 1-based jump coordinates
- `section` is the same parent-breadcrumb label already used by `helpoutlinepick`

This is intentionally tiny. It does not widen docs navigation semantics, invent a richer docs AST, or add a new command. It only gives the existing exact current-doc heading target one explicit inspectable row so humans, scripts, and future UIs can agree on the same answer.

Focused coverage lives in:

- `tests/test_editor_helpjump.py`
- `tests/test_editor_capabilities_registry.py`
