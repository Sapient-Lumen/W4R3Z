# Rev460 — showkey completion reuses exact binding detail

## Why

Micromax already had the right exact binding surface: plain `showkey KEY` gave humans one resolved binding, and `binding_detail_row(KEY)` / `ed.binding-detail-row` gave scripts and future UIs the same exact `[mode key action desc|0 group|0 span|0]` row. But command-bar completion still left `showkey KEY` behind: it did not complete against the reachable binding register at all, so callers had to remember the key exactly or detour through `bindingpick` before asking for one exact binding.

That was a small but real flow/trust mismatch. If one reachable binding already has a tiny honest exact row, ordinary command completion should reuse it too.

## What changed

- `showkey KEY` now completes against the currently reachable binding register
- prompt rows for those candidates now reuse `binding_detail_row(KEY)`
- completion metadata keeps the winner mode, action, optional group, and resolved description visible while choosing a key
- focused tests pin both unique insertion and exact prompt-row metadata

## Effect

This keeps the small key-inspection loop coherent:

- `bindingpick [QUERY]` remains the broad searchable binding browser
- `showkey KEY` remains the tiny exact one-binding surface
- ordinary command completion now bridges those two surfaces instead of making callers guess the key first
