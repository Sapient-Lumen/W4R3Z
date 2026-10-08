# Help-link heading query matching

Rev270 closes the next small docs-browser search gap after rev269.

The grouped pickers already *showed* heading context for docs links:

- docs pages already had visible section headings
- `helplinkpick` could already group rows as `Docs` / `Files` / `External`
- `helpnavpick` already showed heading breadcrumbs on heading rows and appended
  nearest-heading breadcrumbs to visible link-row detail

But filtered **link** queries still only knew about the bare link label plus the
raw target/path. That meant obvious mixed queries like these still failed:

- `helplinkpick External micro editor`
- `helplinkpick Reference Vision ref`
- `helpnavpick External micro editor`

Rev270 keeps the fix tiny and shared:

- docs-link query ranking now uses hidden nearest-heading context from the same
  heading scan the help browser already trusts
- kind labels (`Docs` / `Files` / `External`) are also searchable metadata for
  link rows
- leaf-label hits still win first, so section terms help disambiguate links
  without making heading text outrank the actual link label

Implementation shape:

- new helper `_helplink_query_meta(row)` packages hidden nearest-heading + kind
  metadata for link rows
- new helper `_helplink_row_sort_key(row, query)` keeps the same tiny ranking
  shape as the outline work: label first, then mixed multi-term label+context,
  then context-only fallback
- `help_link_rows(query)` now uses that link-specific sorter instead of the
  older heading-oriented fallback

Focused coverage:

- `tests/test_editor_helplinkpick.py`
- `tests/test_editor_helpnavpick.py`
- `tests/test_mxcontext.py`

Practical effect:

- link pickers now search the same structural context users can already *see*
  in docs pages and grouped picker UI
- future UIs/scripts/LLMs do not need a richer docs AST just to combine a link
  label with its owning section heading
