# Rev471 — `showhooks` completion should reuse tiny hook summary rows

## Why

Micromax already had the right broad live-hook summary surface: `showhooks [QUERY]` and `hook_summary_rows(QUERY)` / `ed.hook-summary-rows` exposed tiny `[name handler_count sample_handler|0 [file line col]|0]` rows for the current live hook namespace. But command-bar completion still rendered `showhooks` queries with a generic `hook summary` placeholder row, which hid the handler count, sample handler, and definition provenance exactly where future humans/LLMs were trying to choose one visible hook.

## What changed

- `showhooks [QUERY]` completion now reuses the same tiny broad-hook summary rows the human command already trusts
- prompt rows keep handler count plus sample handler visible in `menu`
- prompt rows keep hook definition provenance visible in `info` when available
- the fallback stays explicit as `filter hook summary` when the query resolves to no live hook row yet

## Why this shape

This stays deliberately small. `showhook NAME` already had the exact one-hook path through `hook_detail_row(NAME)` / `ed.hook-detail-row`. The remaining seam was narrower: broad `showhooks` completion still lost honest summary metadata even though the summary register already existed. Reusing `hook_summary_rows(QUERY)` keeps the broad command and the prompt on one inspectable substrate without inventing a new host boundary or changing hook execution behavior.
