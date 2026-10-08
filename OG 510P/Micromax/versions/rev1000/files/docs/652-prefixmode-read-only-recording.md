# Rev711 - keep prefixmode read-only while recording

## What changed

- `prefixmode` now lives in `MACRO_NONRECORDABLE_COMMANDS`
- successful `prefixmode MODE` runs no longer append command steps to the macro buffer

## Why

Rev710 fixed the obvious binding-discovery outlier `whichkey`. `prefixmode MODE` was the next nearby command with the same shape: it succeeds by entering a one-shot prefix mode and surfacing reachable bindings, which is useful for discovery but not a replay-worthy automation step.

## New contract

While recording a macro:

- successful `whichkey` output stays out of the macro buffer
- successful `prefixmode MODE` discovery stays out of the macro buffer too
- an ordinary successful command like `goto 1:1` still records exactly once

## Trust/flow impact

This is a small trust and flow cleanup. Binding discovery should help you choose automation, not become the automation.
