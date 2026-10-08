# Rev705 - keep help and apropos read-only while recording

## What changed

- `_macro_should_record_command_name(...)` now treats `help` as non-recordable
- `_macro_should_record_command_name(...)` now treats `apropos` as non-recordable
- running either command during macro recording no longer appends a command step to the macro buffer

## Why

Rev704 fixed a few non-`show` state reporters like `pwd` and `helphistory`. `help` and `apropos` were the next nearby outliers: both are tiny documentation/query commands, but both still became recorded command steps during macro recording.

- `help` points you toward the editor's docs/help entry points
- `apropos QUERY` searches commands/actions/words/docs by name

Neither command performs an automation step worth replaying later.

## New contract

While recording a macro:

- `showstatus` stays out of the macro buffer
- `jumps` stays out of the macro buffer
- `pwd` stays out of the macro buffer
- `helphistory` stays out of the macro buffer
- `help` stays out of the macro buffer
- `apropos QUERY` stays out of the macro buffer
- an ordinary successful command like `goto 1:1` still records exactly once

## Trust impact

This is a small trust cleanup. Documentation/query commands should explain automation, not become part of it.
