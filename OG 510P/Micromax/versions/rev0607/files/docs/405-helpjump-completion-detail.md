# Rev463: helpjump completion now reuses exact heading detail

Micromax already had the right exact docs-navigation substrate before rev463:

- `helpjump QUERY` already resolved one heading on the current docs page with ranked current-doc matching
- `help_heading_detail_row(QUERY)` / `ed.help-heading-detail-row` already exposed that same resolved `[topic title fragment level line col section]` target headlessly
- `helpoutlinepick` / `helpnavpick` already kept richer browse-first docs navigation available when the user wanted to scan more than one heading

But one small flow seam still lingered in the ordinary command-bar loop: typing `helpjump ...` gave no current-doc completion help at all, so the exact heading row existed for scripts and hostcalls while humans still had to remember titles/fragments or reopen a picker.

Rev463 keeps the follow-up deliberately small:

- command-bar completion for `helpjump QUERY` now completes current-doc heading titles plus explicit fragment ids
- prompt rows for those suggestions now reuse `help_heading_detail_row(QUERY)` / `ed.help-heading-detail-row`
- multi-word heading prefixes now complete across the whole `QUERY` span instead of only the last token, so `helpjump Guide L` can complete cleanly to `Guide Links`
- focused prompt-completion tests pin the title, fragment, and metadata contract

The goal is simple: if one docs heading already has a tiny honest exact row, the ordinary `helpjump` loop should reuse it too instead of making the user switch mental modes from “exact target” back to “raw query text.”
