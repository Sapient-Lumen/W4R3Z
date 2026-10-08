# Rev429: tiny shared binding detail row

## What changed

- Added `binding_detail_row(KEY)` in the editor core.
- Added hostcall `ed.binding-detail-row`.
- Plain `showkey KEY` now reuses that same shared row surface.

## Why this is worth doing

Micromax already had the low-level pieces for binding inspection: `ed.resolve-key` and `ed.resolve-key-info` exposed resolved rows, and plain `showkey KEY` gave humans a direct detail line. But the boundary was still slightly ambiguous for scripts and future UIs: there was no *named* machine-facing row that said “this is the exact detail surface behind `showkey`.”

That ambiguity was small, but it mattered for trust and continuity inside an archive:

- humans had one direct inspection command while scripts still had to choose among lower-level resolver helpers
- `showkey` formatting still owned policy that other surfaces could silently drift from
- future UIs/LLMs had no explicit row to point at when they wanted the same one-binding detail humans already saw

Rev429 keeps the fix deliberately tiny. The lower-level resolver hostcalls stay intact, but the editor now also exposes one explicit shared row for the exact human-facing `showkey` surface.

## Row shape

- `binding_detail_row(KEY)` / `ed.binding-detail-row` -> `[mode key action-spec desc|0 group|0 [file line col]|0] | 0`

That shape intentionally matches the visible `showkey` details:

- the resolved winning mode
- the key itself
- the action spec
- the explicit or derived human description
- optional registration group
- optional provenance span

## Relationship to older key resolver hostcalls

This does **not** replace `ed.resolve-key` or `ed.resolve-key-info`. Those stay useful as lower-level resolver helpers. `ed.binding-detail-row` exists so scripts and future UIs can ask a narrower, clearer question:

> what is the exact tiny detail row behind `showkey KEY`?

## Direct user-visible effect

- `showkey KEY` now reuses a named shared row instead of formatting that surface ad hoc
- scripts can inspect one binding through `ed.binding-detail-row` without re-deciding resolver policy
- missing inspection stays explicit through the same `showkey: no such binding: KEY` path

## Follow-up seams

- `binddoc` / `bindmodedoc` / `unbind` success and miss paths are already explicit, but broader “keymap edit preview” or “diff” surfaces are still absent
- bindings still only expose raw action-spec strings rather than a richer parsed action-chain register
- the keybinding docs/search surfaces are still stronger for broad discovery than for tiny grouped/count-aware script snapshots
