# Rev475 — word-topic prompt rows now keep exact definition provenance

## Why

Micromax already had the right exact visible-word surface: `showword NAME` and
`word_detail_row(NAME)` / `ed.word-detail-row` exposed one visible word's
kind/effect/wordlist/summary plus definition provenance. But prompt completion
still kept only the summary in the info slot. That meant `showword`, `help`,
`showtopic`, and `apropos` all hid where a visible Micromax word came from
exactly where future humans/LLMs were deciding whether the word was local,
stdlib, or plugin-loaded.

## What changed

- `_prompt_vm_word_row(...)` now reuses the exact word-detail row more honestly
- prompt info for visible Micromax words now appends `defined at file:line:col`
  when span metadata is available
- `showword NAME`, `help NAME`, and `showtopic NAME` now keep that provenance
  visible during selection
- `apropos QUERY` keeps the same `search topic` cue for word results while also
  appending exact word definition provenance after the summary

## Result

Broad word discovery stays small, but it stops hiding metadata Micromax already
knows. If one visible word already has one tiny honest exact row, the prompt can
reuse that provenance too instead of waiting until after execution.
