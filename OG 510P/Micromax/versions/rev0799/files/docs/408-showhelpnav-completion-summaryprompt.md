# Showhelpnav completion now reuses tiny section-summary rows

## Why

Micromax already had the right broad current-doc navigation bucket surface:
`showhelpnav [QUERY]` / `help_nav_section_summary_rows(QUERY)` /
`ed.helpnav-section-summary-rows` exposed tiny
`[[label count sample_name sample_detail] ...]` rows for visible heading/link
sections like `Top`, breadcrumb-shaped heading buckets, and link families such
as `Docs` / `Files` / `External`. But ordinary command-bar completion still
treated that query slot as opaque text, so humans and future LLMs had to
remember visible bucket labels even though the summary rows already existed one
helper away.

## What changed

- extend the shared section-summary completion helper so it also serves
  `showhelpnav`
- make `showhelpnav [QUERY]` complete visible current-doc navigation section
  labels
- reuse the existing tiny help-navigation summary rows for prompt metadata
  instead of falling back to raw labels
- pin the contract with focused completion tests

## Result

The current-doc navigation summary command now behaves like the newer grouped
summary siblings: if a visible heading/link bucket already has one tiny honest
summary row, command completion reuses it too.
