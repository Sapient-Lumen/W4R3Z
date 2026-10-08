# Rev706 - macro recordability constants

## What changed

- added `MACRO_NONRECORDABLE_COMMANDS`
- added `MACRO_NONRECORDABLE_ACTIONS`
- kept `_macro_should_record_command_name(...)` and `_macro_should_record_action_name(...)` as the thin public helpers over those sets

## Why

Rev702 introduced tiny helper functions for command/action recordability, which already improved clarity. By rev705, though, the concrete names behind those helpers had grown enough that they were becoming policy hidden in conditions again.

Rev706 keeps the visible behavior unchanged and makes the archive easier to scan:

- the non-recordable command names now sit in one small set
- the non-recordable action names now sit in one small set
- the helpers still define the behavioral contract, but the raw names are now obvious before you edit the helpers

## Trust impact

This is mostly an archive-maintenance win. The recording behavior does not change, but the rules behind it are easier to inspect, audit, and extend without accidental drift.
