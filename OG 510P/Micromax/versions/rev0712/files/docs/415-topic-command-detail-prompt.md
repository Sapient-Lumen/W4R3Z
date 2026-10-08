# Rev473 — generic command-topic completion now reuses exact command detail

Micromax already had the right exact command-inspection surface: `showcmd NAME`
and `command_detail_row(NAME)` / `ed.command-detail-row` exposed one command's
doc/group/provenance in one tiny honest row. Generic topic resolution also
already knew how to resolve a visible topic name to that same command.

But one small drift still lingered in the broad help loop: prompt rows for
`help NAME` and `showtopic NAME` still collapsed command topics back to a
generic `help topic` row, which hid group/provenance exactly where a human or
future LLM was deciding whether this visible topic was built in, plugin-owned,
or locally registered.

## What changed

- add a shared `_prompt_action_row(...)` helper so `showaction` and generic
  topic completion stop hand-formatting action rows separately
- make `_prompt_help_topic_row(...)` delegate command topics to
  `_prompt_command_row(...)`
- `help NAME` / `showtopic NAME` command-topic completion now keeps exact
  command doc/group/provenance visible while choosing one visible topic
- focused prompt-completion tests pin that contract for both `help` and
  `showtopic`

## Why it matters

This stays deliberately small. Broad help exploration should not downgrade the
metadata Micromax already trusts for one exact command. If generic topic
resolution already knows a visible topic is a command, the prompt should reuse
that same exact command row instead of hiding the command's origin behind a
placeholder.
