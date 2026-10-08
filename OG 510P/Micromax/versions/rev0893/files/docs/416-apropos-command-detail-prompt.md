# Rev474 — `apropos` command-topic completion now keeps exact command detail

## Why

Micromax already had the right broad discovery surface for `apropos QUERY`: the
prompt reused the same generic topic resolution as `help`, so visible command
topics already carried their exact doc string in the menu slot. But one small
drift still lingered in the info slot: once a visible apropos result resolved to
a command, the prompt threw away the command's exact group/provenance metadata
and flattened the row back to plain `search topic`.

That made the discovery loop slightly less trustworthy than the narrower exact
inspection surfaces right where future humans/LLMs were deciding whether a
visible topic was built in, plugin-provided, or locally registered.

## What changed

- add a tiny `_prompt_topic_search_row(...)` helper for search-driven topic rows
- keep the existing `search topic` cue for `apropos`, but preserve exact command
  metadata after it when the resolved topic is really a command
- leave action topics on the same broad `search topic` dialect unless/until
  actions grow richer exact metadata of their own
- pin the contract with a focused `apropos` command-topic completion test

## Result

Broad discovery stays broad, but it stops hiding metadata Micromax already
knows. If `apropos` already resolved one visible result to one exact command
row, the prompt can keep that command's group/provenance visible while still
marking the row as search-driven.
