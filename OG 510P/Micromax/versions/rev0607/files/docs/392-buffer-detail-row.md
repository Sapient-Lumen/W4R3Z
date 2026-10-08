# Buffer detail row

Rev450 closes one small exact-inspection seam in Micromax's everyday buffer loop.

Micromax already had the right broad buffer surfaces:

- plain `buffers` exposed the active/dirty/readonly/position inventory for humans
- `buffer_inventory_rows()` / `ed.buffer-inventory-rows` exposed that same ordered register to scripts and future UIs
- `bufferpick [QUERY]` / `ed.buffer-section-rows` exposed grouped browse state
- rev447 added `buffer_section_summary_rows(QUERY)` / `ed.buffer-section-summary-rows` / `showbuffergroups [QUERY]` for the lighter broad bucket question

But one small inspectability seam still lingered underneath that model: there was still no official side-effect-free exact answer to the smaller question future humans/LLMs often ask next:

> what is true about this one buffer right now?

The only direct named command was still mutating `buffer NAME`, which switches focus. Scripts could inspect the whole inventory and filter it themselves, but there was no tiny exact register matching a plain human `show...` surface.

Rev450 keeps the follow-up deliberately small:

- add one tiny exact buffer-detail row
- expose it as `ed.buffer-detail-row`
- add one small convenience word, `buffer-detail`
- add one plain side-effect-free human command, `showbuffer NAME`

## Exact row shape

`buffer_detail_row(NAME)` / `ed.buffer-detail-row` return:

```text
[name position active dirty readonly section path line_count]
```

Where:

- `name` is the exact buffer name
- `position` is the current primary cursor label as `line:col`
- `active` / `dirty` / `readonly` are `0` / `1` flags matching the plain `buffers` surface
- `section` is the same visible bucket label grouped buffer discovery already uses (`Help`, `Scratch`, a project root, a parent directory, or `Buffers`)
- `path` is the current backing file path when one exists, else `""`
- `line_count` is the current buffer line count

Example:

```text
['/tmp/demo/proj/file.txt', '2:2', 1, 1, 0, '/tmp/demo/proj', '/tmp/demo/proj/file.txt', 2]
```

The shape intentionally stays small. Full grouped browse state still belongs to `bufferpick` / `ed.buffer-section-rows`, and bulk inventory still belongs to `buffers` / `ed.buffer-inventory-rows`.

## Human command

Plain command-bar inspection gets the same side-effect-free surface:

```text
showbuffer NAME
```

Example:

```text
showbuffer /tmp/demo/proj/file.txt
buffer /tmp/demo/proj/file.txt [active, dirty] @ 2:2 — section=/tmp/demo/proj | /tmp/demo/proj/file.txt | 2 lines
```

Missing names stay explicit instead of falling through to the mutating `buffer NAME` dialect:

```text
showbuffer nope
showbuffer: no such buffer: nope
```

## Why this matters

This is a small trust/flow improvement.

Buffers already had a clean three-scale loop for inventory and grouped browse state, but there was still no first-stop exact inspector for one named buffer. `showbuffer NAME` and `ed.buffer-detail-row` keep that answer inspectable without switching focus, scraping the bulk `buffers` summary, or reopening grouped picker state.

That makes the archive easier to inspect headlessly and keeps buffer discovery aligned with the other exact row surfaces Micromax already exposes for commands, actions, words, docs, topics, options, keymodes, and hooks.

## Focused tests

- `tests/test_editor_buffer_mru_and_closeall.py`
- `tests/test_editor_prompt_completion_hostcalls.py`
- `tests/test_editor_capabilities_registry.py`

## Next tiny seams

- recent files still have flat inventory plus grouped/summary browse surfaces, but not the same tiny exact named row a side-effect-free `showrecent ...` command could reuse
- some other everyday inventories may still rely on plain command formatting even when adjacent grouped/summary layers are now shared
