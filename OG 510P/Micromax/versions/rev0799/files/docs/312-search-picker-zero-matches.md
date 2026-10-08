# rev370 — search picker zero-match submit feedback

Recent trust-first work already made search-first discovery count-aware in plain command output (`apropos QUERY`, `showbindings`, `whichkey`) and made the searchable prompts themselves share stable grouped row models.

That was a good baseline, but one small structural mismatch still lingered in the live submit path for three search-first prompts:

- `commandpick QUERY`
- `topicpick QUERY`
- `bindingpick QUERY`

When a typed query produced zero reachable results, submitting the prompt still fell back to a vague `(none)` message.

That weakened trust in two ways:

- it hid which query just failed
- it spoke a lower-fidelity dialect than nearby count-aware discovery surfaces

## Change

Keep the change deliberately small:

- `commandpick QUERY` now says `commandpick QUERY: 0 match(s)`
- `topicpick QUERY` now says `topicpick QUERY: 0 topic(s)`
- `bindingpick QUERY` now says `bindingpick QUERY: 0 binding(s)`

The success paths, grouped sections, ranking, and row metadata stay exactly as they were.

## Why it matters

Micromax wants live scripting and discovery surfaces that stay inspectable and boringly honest.

These search-first prompts are part of that loop:

- future UIs can open them
- scripts can prefill them
- LLMs can reason about them without guessing what `(none)` meant

The tiny goal here is simple: when a search-first picker has zero reachable results, the submit path should still tell the truth in a structurally explicit way.
