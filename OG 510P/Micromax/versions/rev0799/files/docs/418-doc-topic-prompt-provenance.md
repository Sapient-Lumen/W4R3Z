# Rev476 — doc-topic prompt rows now keep docs path and search cue

## Why

Micromax already had the right exact visible-doc surface: `showdoc NAME` and
`doc_detail_row(NAME)` / `ed.doc-detail-row` exposed one docs topic's title,
summary, section family, and backing path. But prompt completion still hid a
small part of that truth. `showdoc`, `help docs`, generic `help` /
`showtopic`, and even `apropos` all showed the docs title and summary, yet they
still dropped the backing docs path exactly where future humans/LLMs were
deciding whether one visible topic came from the vision docs, portability
notes, or a newer handoff page.

`apropos` had one extra drift too: doc topics stayed indistinguishable from
exact topic lookup because the prompt never kept the existing `search topic`
cue for docs the way recent command/word rows now do.

## What changed

- `_prompt_doc_row(...)` now appends the backing docs path from
  `doc_detail_row(NAME)` when it is known
- `showdoc NAME`, `help docs NAME`, generic `help NAME`, and `showtopic NAME`
  now keep that docs path visible during selection
- `apropos QUERY` doc-topic rows now preserve the same `search topic` cue while
  keeping docs section/summary/path metadata visible
- `_prompt_topic_search_row(...)` now treats generic placeholder info strings
  honestly so broad discovery does not emit awkward `search topic · help topic`
  fallbacks

## Result

Broad doc discovery stays small, but it stops hiding which doc file backs one
visible topic. If Micromax already knows the exact docs row for one topic, the
prompt can keep that path visible too instead of waiting until after execution.
