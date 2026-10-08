# Rev459 — keymode completion rows reuse exact keymode detail

## What changed

Micromax already had the right exact keymode inspection surface:

- plain `showkeymode NAME` reported one visible or currently active keymode directly
- `keymode_detail_row(NAME)` / `ed.keymode-detail-row` exposed that same exact row to scripts and future UIs
- `showkeymodes` / `ed.keymode-inventory-rows` already covered the broader active-vs-known inventory

But one small trust/flow drift still remained in the command bar itself: keymode-oriented completion rows still used a more generic placeholder shape than nearby exact-inspection completions like `showhook`, `showplugin`, `showjump`, or `showrecentdir`.

That meant the user could tab through the right mode names, but the completion row stopped showing the exact state Micromax already knew:

- whether the mode was currently active
- whether it was one-shot
- whether it was a visible durable mode or a transient internal one
- how many bindings it currently had
- what one representative binding looked like

Rev459 keeps the fix deliberately small.

## What landed

- add one shared `_prompt_keymode_row(...)` helper in the editor core
- make `showkeymode NAME` completion reuse `keymode_detail_row(NAME)`
- make `showbindings MODE` completion reuse the same exact keymode metadata for concrete mode names
- make `keymode`, `pushkeymode`, `pushkeymode-once`, and `prefixmode` reuse that same row too

The row shape presented to completion stays the normal prompt tuple:

```text
[insert kind menu info]
```

But `menu`/`info` now carry exact keymode detail instead of a generic label, for example:

```text
['goto ', 'keymode', 'known bindings=1', 'g->command:showstatus (show portable statusline summary)']
```

Or for an active transient internal mode:

```text
['prompt ', 'keymode', 'active once internal bindings=N', 'sample-binding...']
```

## Why this matters

This is intentionally a tiny follow-up, but it lands at a good trust/flow seam.

Micromax already had an honest exact row for one keymode. The command bar was
just failing to reuse it at the moment where users, scripts, and future LLMs
actually choose a mode name. Reusing the same row buys three small wins at once:

- completion stops degrading exact keymode state into a generic placeholder
- keymode-push and keymode-inspection commands feel more coherent with the rest of the newer exact-row work
- future command-bar UIs can rely on one shared substrate instead of re-deriving mode state ad hoc

The goal is simple: exact inspection and completion should speak the same tiny dialect.

## Focused tests

- `tests/test_editor_prompt_completion_hostcalls.py`
- `tests/test_editor_transient_keymodes.py`
