# Rev437 — exact generic help topics get one tiny named row

## What changed

Micromax already had a good generic help-discovery loop:

- `help_topic_rows()` / `ed.topic-rows` exposed commands, actions, visible words, and docs topics together
- `apropos_rows()` / `ed.apropos-rows` ranked that same shared topic set for search
- `ed.topic-section-rows` / `ed.apropos-section-rows` made broad grouped browse paths inspectable
- narrower exact detail rows already existed for commands, actions, words, and docs pages

But one tiny inspectability seam still remained: once a human, script, or future UI already knew the generic topic name it cared about, there was still no *single* exact generic-topic surface. Callers still had to search `ed.topic-rows` / `ed.apropos-rows` or branch across `showcmd` / `showaction` / `showword` / `showdoc` before asking what one known topic resolved to.

Rev437 keeps the fix deliberately small:

- add `topic_detail_row(NAME)` in the editor core
- expose it as hostcall `ed.topic-detail-row`
- add plain `showtopic NAME` for humans
- reuse that same generic topic metadata for `showtopic` command completion

## Row shape

`topic_detail_row(NAME)` / `ed.topic-detail-row` return:

```
[name kind detail_row]
```

Where `kind` is one of:

- `command`
- `action`
- `word`
- `doc`

And `detail_row` is the same narrower exact row already returned by the existing kind-specific helpers:

- `command_detail_row(NAME)` / `ed.command-detail-row`
- `action_detail_row(NAME)` / `ed.action-detail-row`
- `word_detail_row(NAME)` / `ed.word-detail-row`
- `doc_detail_row(TOPIC)` / `ed.doc-detail-row`

Resolution intentionally follows the same precedence humans already trust through `help NAME`:

1. command
2. action
3. visible word
4. docs topic

Returns `0` when the target does not resolve to any known generic help topic.

## Why this matters

This is a small trust/flow improvement. Generic help topics were already first-class for search, but exact inspection still required a second branching step. `showtopic NAME` and `ed.topic-detail-row` close that seam with one small side-effect-free surface:

- humans can inspect one known topic without reopening docs pages
- scripts and future UIs can ask one direct question before branching on the answer
- generic discovery stays aligned with the narrower exact detail rows already trusted elsewhere in the archive

## Focused tests

- `tests/test_editor_mx_commands_and_completion.py`
- `tests/test_editor_prompt_completion_hostcalls.py`
- `tests/test_editor_capabilities_registry.py`

## Next tiny seams

- broader help/topic grouped snapshots are still stronger for browse/search than for tiny count-aware section summaries
- docs/help discovery now has strong exact page/heading/link/topic inspection, but broader section-level docs/topic inventory is still thinner than those exact surfaces
