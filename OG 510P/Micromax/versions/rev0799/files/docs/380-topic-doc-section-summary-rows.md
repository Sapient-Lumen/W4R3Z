# Rev438 — broad help/docs section summaries get one tiny named row shape

## What changed

Micromax already had strong broad help/docs discovery:

- `help_topic_rows()` / `ed.topic-rows` and `apropos_rows()` / `ed.apropos-rows` exposed generic help topics
- `ed.topic-section-rows` / `ed.apropos-section-rows` grouped those topics into browseable families
- `doc_prompt_rows()` / `ed.doc-rows` and `ed.doc-section-rows` exposed docs topics and numbered docs families
- recent revs added exact detail rows for commands, actions, words, docs pages, docs headings, docs links, and exact generic topics

But one small inspectability seam still remained: broad discovery families were easy to browse and search, yet there was still no tiny count-aware answer for what major topic/doc sections currently exist without walking every grouped row or scraping picker headers.

Rev438 keeps the fix deliberately small:

- add `help_topic_section_summary_rows()` in the editor core
- add `apropos_section_summary_rows(QUERY)` in the editor core
- add `doc_section_summary_rows(QUERY)` in the editor core
- expose them as `ed.topic-section-summary-rows`, `ed.apropos-section-summary-rows`, and `ed.doc-section-summary-rows`
- add plain `showtopics` and `showdocs` for humans

## Row shape

All three helpers return the same tiny row shape:

```
[label count sample_name sample_detail]
```

Where:

- `label` is the visible section/family label
- `count` is the number of rows currently in that section
- `sample_name` reuses the first visible item in that section
- `sample_detail` reuses the first visible row's detail text (`info` when present, otherwise `menu`)

Examples:

- topic summaries: `Commands`, `Actions`, `Words`, `Docs`
- docs summaries: `00–09 Project`, `10–19 Research`, `20–29 Language + VM`, ...

The shape is intentionally tiny. It complements the fuller grouped section rows instead of replacing them.

## Why this matters

This is a small trust/flow improvement. Broad discovery surfaces were already first-class for browse/search, but there was still no official small register for the simpler question future humans/LLMs often ask first:

> what broad help/docs sections exist right now?

The new summary rows and plain commands keep that answer inspectable without reopening docs, walking every grouped row, or scraping section headers out of picker output.

## Focused tests

- `tests/test_editor_mx_commands_and_completion.py`
- `tests/test_editor_capabilities_registry.py`

## Next tiny seams

- some other grouped picker families still only expose their full grouped row shapes and not a lighter summary sibling
- broad help/docs summaries are now honest, but richer query-aware summary/diff helpers for other inventories may still be useful later
