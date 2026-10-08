# Rev703 - keep jumps read-only while recording

## What changed

- `_macro_should_record_command_name(...)` now treats `jumps` as non-recordable
- running `jumps` during macro recording no longer appends a command step to the macro buffer

## Why

Rev699 drew a clear line for the `show*` inspector family: observational commands should not rewrite the macro they are observing.

`jumps` was a tiny outlier next door. It is just the jumplist register viewer, but because it does not start with `show`, it still slipped through the recordability filter and became a recorded command step.

## New contract

While recording a macro:

- `showstatus` stays out of the macro buffer
- `jumps` stays out of the macro buffer too
- an ordinary successful command like `goto 1:1` still records exactly once

## Trust impact

This is a small trust cleanup. Register viewers should observe automation state, not become part of it.
