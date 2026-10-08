# Rev704 - keep pwd and helphistory read-only while recording

## What changed

- `_macro_should_record_command_name(...)` now treats `pwd` as non-recordable
- `_macro_should_record_command_name(...)` now treats `helphistory` as non-recordable
- running either command during macro recording no longer appends a command step to the macro buffer

## Why

Rev703 fixed one clear non-`show` inspection outlier: `jumps` is a register viewer, so it should not record itself into macros. `pwd` and `helphistory` were the next two tiny state-reporting commands with the same problem.

- `pwd` reports the current working directory
- `helphistory` reports the docs help-history register

Neither command performs an automation step worth replaying later.

## New contract

While recording a macro:

- `showstatus` stays out of the macro buffer
- `jumps` stays out of the macro buffer
- `pwd` stays out of the macro buffer
- `helphistory` stays out of the macro buffer
- an ordinary successful command like `goto 1:1` still records exactly once

## Trust impact

This is a small trust cleanup. Tiny state-reporting commands should observe state, not become part of the automation they are describing.
