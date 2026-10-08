# Rev467 — option/plugin grouped-summary completion now reuses tiny summary rows

Micromax already had two broad grouped-summary surfaces that were structurally honest once you ran them:

- `showoptiongroups [QUERY]` / `option_section_summary_rows(QUERY)` / `ed.option-section-summary-rows`
- `showplugins [QUERY]` / `plugin_section_summary_rows(QUERY)` / `ed.plugin-section-summary-rows`

Both surfaces already exposed the tiny shared summary shape `[[label count sample_name sample_detail] ...]`, so humans, scripts, and future UIs could ask which visible option families or plugin-state buckets existed without opening the heavier grouped pickers.

But one small prompt-loop drift still lingered next to that model: command-bar completion for those broad summary commands still treated the query as opaque text. That meant users could *see* buckets like `Capabilities` or `Loaded` once the command ran, but the command bar itself could not help them choose those same visible labels with the matching count/sample metadata.

Rev467 keeps the fix deliberately small:

- `showoptiongroups [QUERY]` now completes visible option-family labels and reuses the same tiny summary rows in prompt suggestions
- `showplugins [QUERY]` now completes visible plugin-state bucket labels and reuses the same tiny summary rows in prompt suggestions
- the shared grouped-summary prompt helper now covers those two remaining summary commands instead of only the more recent buffer/recent/mark/palette/helpnav family
- focused prompt-completion tests pin both metadata contracts

The goal is simple: if a broad grouped-summary command already has one tiny honest row for each visible bucket, command completion should reuse that same row instead of hiding the bucket behind a raw label.
