# Plugin runtime zero-error state witness

## Goal

Keep filtered runtime `plugin info NAME` and `plugin errors NAME` feedback concrete when Micromax already knows the named plugin is a real on-disk candidate that is not currently loaded.

## Problem

After the exact command-bar rows learned to say `available plugin · not loaded`, the runtime zero-error path still flattened the same state back to bare `errors: 0`.

That made two adjacent trust-sensitive paths disagree:

- exact completion already kept the available-candidate witness
- after Enter, filtered runtime feedback hid it again

## Change

Add one tiny shared runtime suffix helper in `command_dispatcher.py` and let filtered zero-error lines append it only for known available-but-unloaded targets.

Examples:

- `plugin errors optional` → `errors: 0 · available plugin · not loaded`
- `plugin info optional` → final line `errors: 0 · available plugin · not loaded`
- healthy loaded plugins still keep plain `errors: 0`

## Why this shape

This keeps the runtime path aligned with nearby exact plugin inspection without making the common loaded case noisier or widening the host boundary.
