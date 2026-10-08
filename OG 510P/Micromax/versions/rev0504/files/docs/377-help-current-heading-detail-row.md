# Rev435: current docs-heading detail row

Micromax already had good docs-heading surfaces before rev435:

- `helpoutlinepick` / `helpnavpick` exposed searchable heading rows for the current docs page
- `helpjump QUERY` already reused that same ranking logic for exact heading targets
- `help_heading_detail_row(QUERY)` / `ed.help-heading-detail-row` already exposed the exact jump target as one tiny inspectable row

But one tiny inspectability seam still lingered underneath that loop: neither humans nor scripts had a named first-stop way to ask which heading currently owned the cursor in the open docs buffer. That left callers scraping `help_outline_rows()` again or inferring context from breadcrumbs and status text.

Rev435 keeps the fix deliberately small:

- add `current_help_heading_detail_row()` in the editor core
- expose it as hostcall `ed.help-current-heading-detail-row`
- add `showhelpheading` as the human-facing sibling for that exact current-heading row

The row shape is:

- `[topic title fragment level line col section]`

Where:

- `topic` is the current docs topic
- `title` is the nearest heading text owning the primary cursor
- `fragment` is the resolved explicit or auto heading fragment id
- `level` is the markdown heading level (`1..6`)
- `line` / `col` are the 1-based heading coordinates
- `section` is the same parent-breadcrumb label already used by `helpoutlinepick`

This is intentionally tiny. It does not widen docs navigation semantics, add a richer docs AST, or invent another picker. It only gives the already-known current docs heading one explicit inspectable row so humans, scripts, and future UIs can agree on the same answer.

Focused coverage lives in:

- `tests/test_editor_helpjump.py`
- `tests/test_editor_capabilities_registry.py`
- `tests/test_editor_mx_commands_and_completion.py`
