# Generic help/apropos docs topics

Rev432 tightens one small discovery seam in Micromax's help/docs loop.

Micromax already had good docs-specific discovery:

- `help docs TOPIC` opened exact docs pages
- `helppick` / `ed.doc-rows` / `ed.doc-section-rows` exposed searchable docs rows
- `showdoc TOPIC` / `ed.doc-detail-row` exposed one exact docs detail row

But generic topic discovery still treated docs as a second search universe.
`help_topic_rows()` / `ed.topic-rows`, `apropos_rows()` / `ed.apropos-rows`,
plain `help QUERY` / `apropos QUERY` completion, and `topicpick` only
advertised commands/actions/words unless the caller had already switched into a
docs-specific path.

That made the archive harder to trust and harder for future humans/LLMs to
continue:

- `help vision` worked, but generic completion could hide `vision`
- `topicpick` felt like a whole-project discovery surface, but docs were absent
- scripts inspecting `ed.topic-rows` still had to remember a second docs-only API

The rev432 fix stays deliberately small:

- `help_topic_rows()` now appends the same docs rows already used by the docs picker
- `_prompt_help_topic_names()` now includes docs topics too
- generic `help` / `apropos` suggestion rows reuse `_prompt_doc_row()` when the
  candidate resolves to a docs topic
- `apropos_rows()` keeps deterministic ties honest by still preferring
  commands/actions/words before docs when the textual score is otherwise equal

The intent is simple: docs topics should be first-class in the ordinary
help/search loop, not a hidden second search universe.
