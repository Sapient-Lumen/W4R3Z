# Keymode detail row (rev442)

Rev442 closes one small symmetry gap in Micromax's keymap discovery loop.

Micromax already had the right **broad** keymode surface:

- plain `showkeymodes` for humans
- `ed.keymode-inventory-rows` for scripts and future UIs
- lower-level per-mode binding rows when a caller already knew which mode mattered

But one small inspectability seam still lingered underneath that model: future humans/LLMs could answer *what keymodes exist right now?* yet still had to join multiple surfaces just to answer the next exact question:

> tell me about **this one keymode** right now

That is exactly the kind of tiny follow-up that should have one stable named row.

## New shared row

```text
keymode_detail_row(NAME)
ed.keymode-detail-row
```

Returns:

```text
[mode active? known? once? binding_count sample_key|0 sample_action|0 sample_desc|0] | 0
```

Where:

- `mode` is the queried keymode name
- `active?` is `1` when the mode is currently on the active stack
- `known?` is `1` when the mode belongs to the visible durable keymode list used by `showkeymodes`
- `once?` is `1` when the active mode is one-shot / transient
- `binding_count` is the current number of exact mode-local bindings
- `sample_*` expose one stable first binding when one exists, otherwise `0`

The resolution policy stays intentionally small and honest:

- visible known modes are inspectable even when inactive
- currently active internal/capture modes are inspectable too
- unknown inactive names return `0` / `showkeymode: no such keymode: NAME`

## New plain command

```text
showkeymode NAME
```

Examples:

```text
keymode goto [active once known] bindings=1 sample=g->command:showstatus (show portable statusline summary)
keymode prompt [active once internal] bindings=0
keymode global [known] bindings=0
```

## Why this helps

This is a trust/flow change, not a larger keymap redesign.

It keeps Micromax's keymap discovery surfaces structurally consistent:

- broad register: `showkeymodes` / `ed.keymode-inventory-rows`
- exact register: `showkeymode NAME` / `ed.keymode-detail-row`

That means future humans, scripts, and LLMs no longer need to reconstruct one mode's state by joining inventory rows with lower-level binding rows just to answer a small exact question.
