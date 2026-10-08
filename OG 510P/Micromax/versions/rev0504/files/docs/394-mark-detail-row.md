# Mark detail row

Rev452 closes one small exact-inspection seam in Micromax's everyday mark loop.

Micromax already had the right broad mark surfaces:

- plain `marks` exposed the active/here/preview-aware inventory for humans
- `mark_inventory_rows()` / `ed.mark-inventory-rows` exposed that same ordered register to scripts and future UIs
- `markpick [QUERY]` / `ed.mark-section-rows` exposed grouped browse state by owning buffer

But one small inspectability seam still lingered underneath that model: there was still no official side-effect-free exact answer to the smaller question future humans/LLMs often ask next:

> what is true about this one mark right now?

The only direct named command was still mutating `markjump NAME`, which changes buffers/cursor and pushes the jumplist. Scripts could inspect the whole inventory and filter it themselves, but there was no tiny exact register matching a plain human `show...` surface.

Rev452 keeps the follow-up deliberately small:

- add one tiny exact mark-detail row
- expose it as `ed.mark-detail-row`
- add one small convenience word, `mark-detail`
- add one plain side-effect-free human command, `showmark NAME`

## Exact row shape

`mark_detail_row(NAME)` / `ed.mark-detail-row` return:

```text
[name buffer position preview active here]
```

Where:

- `name` is the exact mark name
- `buffer` is the owning buffer name
- `position` is the anchored target as a small 1-based `line:col` label
- `preview` is the trimmed source-line preview when the target buffer is still open
- `active` is `1` when the mark belongs to the current buffer
- `here` is `1` when the mark matches the current primary cursor exactly

Example:

```text
['here', 'alpha', '2:0', 'target', 1, 1]
```

The shape intentionally stays small. Full grouped browse state still belongs to `markpick` / `ed.mark-section-rows`, and bulk inventory still belongs to `marks` / `ed.mark-inventory-rows`.

## Human command

Plain command-bar inspection gets the same side-effect-free surface:

```text
showmark NAME
```

Example:

```text
showmark here
mark here -> *alpha [here] @ 2:0 — target
```

Missing names stay explicit instead of falling through to the mutating `markjump NAME` dialect:

```text
showmark nope
showmark: no such mark: nope
```

## Why this matters

This is a small trust/flow improvement.

Marks already had a clean three-scale loop for inventory and grouped browse state, but there was still no first-stop exact inspector for one named mark. `showmark NAME` and `ed.mark-detail-row` keep that answer inspectable without jumping through the mark, scraping the bulk `marks` summary, or reopening grouped picker state.

That makes the archive easier to inspect headlessly and keeps mark discovery aligned with the other exact row surfaces Micromax already exposes for commands, actions, words, docs, topics, options, buffers, keymodes, hooks, and recent files.

## Focused tests

- `tests/test_editor_marks.py`
- `tests/test_editor_prompt_completion_hostcalls.py`
- `tests/test_editor_capabilities_registry.py`

## Next tiny seams

- jump history already has flat inventory plus grouped browse state, but one exact side-effect-free jump-row inspector may still be useful if future UIs/LLMs keep needing to ask about one named jump entry without selecting it
- some other everyday inventories may still rely on plain command formatting even when adjacent grouped/summary layers are now shared
