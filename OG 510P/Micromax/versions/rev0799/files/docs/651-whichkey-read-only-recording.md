# Rev710 - keep whichkey read-only while recording

## What changed

- `whichkey` now lives in `MACRO_NONRECORDABLE_COMMANDS`
- successful `whichkey` runs no longer append command steps to the macro buffer

## Why

Rev703 through rev709 cleaned up most observer and discovery surfaces, but `whichkey` was still a successful outlier. It can render the active binding inventory and return success, which meant it still became a recorded macro step even though it is purely a discovery surface.

## New contract

While recording a macro:

- successful `whichkey` output stays out of the macro buffer
- other observer/query families like `show*`, `help*`, and `*pick` still stay out too
- an ordinary successful command like `goto 1:1` still records exactly once

## Trust/flow impact

This is a small trust and flow cleanup. Binding discovery should help you inspect automation, not become the automation.
