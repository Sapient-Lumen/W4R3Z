# Revision 0284 — qutebrowser userscript pack

This revision turns another app-native planner lane into a concrete export.

## What changed

- added `vhk gen-qutebrowser-pack`
- added `src/vhk/project/qutebrowser_pack.py`
- added `tests/test_qutebrowser_pack_cli.py`
- updated app-native planner command wiring so qutebrowser-targeted projects now point at a real pack
- added a qutebrowser-specific `plan-project` test slice
- updated:
  - `docs/SPECS.md`
  - `docs/PLAN_2026.03.17_LINUX_NATIVE_AHK_PARITY.md`
  - `docs/ISSUES_2026Q1.md`

## Why this matters

VHK already recognized qutebrowser as an app-native target, but the lane still
stopped at prose. This revision makes that lane reviewable and runnable through
thin userscript wrappers that keep qutebrowser in charge of browser-facing
entry/context while VHK keeps macro semantics.

## What the new pack writes

- `vhk.qutebrowser.routes.yml`
- `vhk.qutebrowser.commands.json`
- `userscripts/*`
- `README.md`

The generated userscripts:

- can be launched with `:spawn --userscript ...`
- can also be launched from hint mode with `:hint links userscript ...`
- forward qutebrowser `QUTE_*` context into `vhk run ... --vars ...`
- optionally emit `message-info` / `message-error` feedback via `QUTE_FIFO`

## Remaining honest gap

This first pack deliberately stays thin:

- it exports browser-targeted entrypoints, not a richer qutebrowser-specific DSL
- it does not yet synthesize dedicated hint userscript variants or browser-side
  command templates from macro intent
- future Studio/inspector work should help authors capture userscript names,
  hint-mode assumptions, and browser-context expectations directly instead of
  reconstructing them from docs
