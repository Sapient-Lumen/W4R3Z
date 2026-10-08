# Rev616: keep plain `showbuffer` truthful at the root

## Why this tiny change matters

Micromax already had the important nearby pieces:

- `buffer_detail_row(NAME)` / `ed.buffer-detail-row` exposed exact buffer truth
  for one name.
- `buffer_inventory_rows()` / `buffers` already exposed the live buffer
  register headlessly and at runtime.
- neighboring exact inspectors like `showoption`, `showcmd`, `showaction`,
  `showword`, and `showkey` had already learned to keep one live inventory
  witness visible before and after Enter.

But one narrow adjacent seam still lingered in the buffer-inspection loop:
plain `showbuffer` still fell back to generic command metadata before Enter,
and raw runtime `showbuffer` still jumped straight to `usage: showbuffer NAME`
even though Micromax already knew the current buffer set it was asking the user
to inspect.

That made the exact buffer inspector feel thinner than the surrounding trust
surfaces at the exact moment a human or LLM most wants confidence about the
current working set.

## What changed

Rev616 keeps the fix deliberately small and compatible:

- new shared `_buffer_inventory_preview_summary()` keeps one compact live
  buffer witness on one tiny substrate
- the summary prefers active or dirty non-scratch buffers when present so real
  work buffers stay visible ahead of `*scratch*`
- plain `showbuffer` command-bar completion now reuses that same root summary
- raw runtime `showbuffer` now prints that same summary before
  `usage: showbuffer NAME`
- focused prompt/runtime tests pin the no-arg root behavior

## Example shape

With one active dirty file buffer loaded, plain `showbuffer` can now surface:

```text
showbuffer: 2 buffers · /tmp/proj/root.txt [active, dirty] @ 2:1 — /tmp/proj/root.txt | 3 lines
usage: showbuffer NAME
```

That keeps the exact inspector usage-shaped while still telling the truth about
which buffer state is live right now.

## Verification

Focused coverage lives in:

- `tests/test_editor_buffer_mru_and_closeall.py`
- `tests/test_editor_prompt_completion_hostcalls.py`
- `tests/test_mxcontext.py`
- `tests/test_mkrevzip.py`
