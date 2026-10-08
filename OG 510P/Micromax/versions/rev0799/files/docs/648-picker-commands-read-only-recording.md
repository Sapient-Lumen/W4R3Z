# Rev707 - keep picker commands read-only while recording

## What changed

- `_macro_should_record_command_name(...)` now treats commands ending in `pick` as non-recordable
- picker openers like `commandpick`, `helppick`, and `jumppick` no longer append command steps to the macro buffer

## Why

Rev703 through rev705 cleaned up obvious read-only inspection/query commands. The remaining nearby outlier family was the searchable picker surface.

Commands ending in `pick` are there to help the user explore choices in a prompt or picker. That is useful UI, but it is not a stable automation step worth replaying later inside a recorded macro.

## New contract

While recording a macro:

- `show*` inspectors stay out of the macro buffer
- non-`show` observers like `jumps`, `pwd`, `helphistory`, `help`, and `apropos` stay out of the macro buffer
- picker openers like `commandpick`, `helppick`, and `jumppick` stay out of the macro buffer too
- an ordinary successful command like `goto 1:1` still records exactly once

## Trust/flow impact

This is a small trust and flow cleanup. Searchable pickers should help you choose automation, not become the automation.
