# Rev382 — typed help/doc misses

## What changed

The editor-side `help` command now keeps its own surface name visible when lookup fails.

- `help docs TOPIC` now reports `help docs: no such doc: TOPIC`
- general `help QUERY` misses now report `help: no such topic: QUERY`
- when apropos-style suggestions exist, the same typed prefix stays in front of the `Try: ...` preview

## Why it matters

This is a tiny trust/flow cleanup. `help` is one of the first discovery surfaces both humans and future LLMs reach for, so its failure wording should match the rest of the editor's newer `surface: no such kind: target` dialect instead of falling back to older prose like `No doc for ...` or `No help for ...`.

## Notes

The successful `help` paths stay unchanged:

- command/action/word help still shows the matching topic
- docs fallback still opens the matching docs page
- suggestion previews still come from the same ranked `apropos` rows
