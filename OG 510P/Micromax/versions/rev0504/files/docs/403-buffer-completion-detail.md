# Rev461 — buffer completion reuses exact buffer detail

## Why

Micromax already had the right exact buffer surface: plain `showbuffer NAME` gave humans one tiny side-effect-free buffer summary, and `buffer_detail_row(NAME)` / `ed.buffer-detail-row` gave scripts and future UIs the same exact `[name position active dirty readonly section path line_count]` row. But ordinary `buffer NAME` completion still lagged behind that exact surface: it fell back to the older generic prompt row, so callers had to choose a buffer without seeing the same active/dirty/readonly/position detail they could inspect one command later.

That was a small but real trust/flow mismatch. If one open buffer already has a tiny honest exact row, the ordinary buffer-switching prompt should reuse it too.

## What changed

- `buffer NAME` completion now reuses `buffer_detail_row(NAME)`
- prompt rows keep section, active/dirty/readonly flags, current position, path, and line count visible while choosing one open buffer
- `showbuffer NAME` completion now reuses that same exact helper too, so the two named-buffer command paths stay aligned
- focused tests pin both the inspect-only and switch-buffer completion metadata contracts

## Effect

This keeps the small buffer-navigation loop coherent:

- `bufferpick [QUERY]` remains the broad searchable buffer browser
- `showbuffer NAME` remains the tiny exact one-buffer inspection surface
- ordinary `buffer NAME` completion now bridges those two surfaces instead of degrading back to a thinner prompt row
