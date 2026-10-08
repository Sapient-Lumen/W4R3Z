# Showpalettegroups completion now reuses tiny section-summary rows

## Why

Micromax already had the right broad command-palette bucket surface:
`showpalettegroups [QUERY]` / `command_palette_section_summary_rows(QUERY)` /
`ed.command-palette-section-summary-rows` exposed tiny
`[[label count sample_name sample_detail] ...]` rows for visible `Recent Files`
/ `Recent` / `Commands` / `Actions` palette buckets. But ordinary
command-bar completion still treated that query slot as opaque text, so humans
and future LLMs had to remember visible bucket labels even though the summary
rows already existed one helper away.

## What changed

- extend the shared section-summary completion helper so it also serves
  `showpalettegroups`
- make `showpalettegroups [QUERY]` complete visible palette section labels
- reuse the existing tiny palette summary rows for prompt metadata instead of
  falling back to raw labels
- pin the contract with focused completion tests

## Result

The command palette's broad bucket summary command now behaves like the newer
buffer/recent/mark grouped-summary siblings: if a visible bucket already has
one tiny honest summary row, command completion reuses it too.
