# Help outline section groups

Rev144 taught the docs-focused pickers how to keep multiple visible sections in
view during empty-query browsing, and later picker/status work taught the live
prompt, TUI headers, and headless status surfaces to reuse those same visible
section labels.

`helpoutlinepick` was still the small outlier.

It already knew how to list headings, but the live picker was still one long flat
`Headings` bucket, so future UIs/scripts/LLMs could not ask simple questions like:

- which parent section owns this heading row?
- can the empty-query outline picker keep more than one heading region visible?
- what exact section label should prompt previews/status surfaces show for a deep
  nested heading?

Rev266 keeps the change tiny:

- empty-query `helpoutlinepick` now flattens grouped sections instead of one flat
  heading list
- grouped sections are exposed headlessly through
  `help_outline_section_rows(query)` and hostcall `ed.help-outline-section-rows`
- section labels are the **parent heading breadcrumb** for each heading row
  (`Top`, document title, `Guide`, `Guide › Links`, ...)
- prompt previews, sticky headers, `Alt-Up` / `Alt-Down`, and status surfaces
  now reuse those same visible labels

That keeps the outline picker aligned with the rest of the shared grouped-picker
substrate without changing the row shape or inventing a larger docs AST.

## Guide

This heading exists as the small H2 parent bucket for the nested outline rows
below.

### Links

Nested headings should move into the parent breadcrumb section rather than stay
inside one generic `Headings` bucket.

#### Deep dive

This heading exists to prove that deeper outline rows reuse the full parent path
in both the picker UI and headless status surfaces.

### Other

Sibling nested headings should share the same parent section label.

## Appendix

Later H2/H3 groups should not erase the simpler parent bucket.

## Why this stays honest

This is still not a richer outline tree widget or a full markdown block model.
It is one more small shared grouping surface built from the same heading scan the
help browser already trusts for fragment jumps and outline rows.
