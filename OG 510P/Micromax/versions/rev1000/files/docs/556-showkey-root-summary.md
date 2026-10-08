# Rev615: keep plain `showkey` truthful at the root

## Why this tiny change matters

Micromax already had the important nearby pieces:

- `binding_detail_row(KEY)` / `ed.binding-detail-row` exposed exact resolved
  binding truth for one key.
- `available_binding_inventory_rows()` / `showbindings active` / `whichkey`
  already exposed the live reachable binding register headlessly and at runtime.
- neighboring exact inspectors like `showhook`, `showkeymode`, `showoption`,
  `showcmd`, `showaction`, and `showword` had already learned to keep one live
  inventory witness visible before and after Enter.

But one narrow adjacent seam still lingered in the binding-inspection loop:
plain `showkey` still fell back to generic command metadata before Enter, and
raw runtime `showkey` still jumped straight to `usage: showkey KEY` even though
Micromax already knew the reachable binding inventory it was asking the user to
inspect.

That made the exact binding inspector feel thinner than the surrounding trust
surfaces at the exact moment a human or LLM most wants confidence about the
current keymap.

## What changed

Rev615 keeps the fix deliberately small and compatible:

- new shared `_binding_inventory_preview_summary()` keeps one compact live
  reachable-binding witness on one tiny substrate
- the summary prefers once/non-global winners when present so modal and prefix
  state stays visible instead of disappearing behind a global default binding
- plain `showkey` command-bar completion now reuses that same root summary
- raw runtime `showkey` now prints that same summary before `usage: showkey KEY`
- focused prompt/runtime tests pin the no-arg root behavior

## Example shape

With an active `nav` mode binding loaded, plain `showkey` can now surface:

```text
showkey: 1 binding · Ctrl-g@nav->command:showkeymodes (enter goto map)
usage: showkey KEY
```

That keeps the exact inspector usage-shaped while still telling the truth about
which binding inventory is live right now.

## Verification

Focused coverage lives in:

- `tests/test_editor_keybinding_docs.py`
- `tests/test_editor_prompt_completion_hostcalls.py`
- `tests/test_mxcontext.py`
- `tests/test_mkrevzip.py`
