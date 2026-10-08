# Rev701 - action recording keeps only successful actions

## What changed

- `run_action(...)` now prepares the possible action step up front but appends it only after the action returns success
- blocked mutating actions no longer enter the macro buffer
- successful actions still record exactly once with the same payload shape as before

## Why

Rev700 fixed the command-line side of macro honesty: failed commands should not become recorded automation. The same issue still existed for direct action execution.

Before rev701, Micromax could record an action step even when the action was refused — for example, trying `InsertText` in a read-only buffer. That made the saved macro claim an edit happened when the editor had explicitly blocked it.

## New contract

While recording a macro:

- a blocked read-only mutation like `InsertText` does **not** become a recorded step
- the first successful `InsertText` does become a recorded step
- stopping the macro saves only the actions that actually ran

## Directly pinned

Starting from an empty recording:

- `InsertText` in a read-only buffer leaves the macro buffer at `0`
- turning off readonly and running `InsertText` grows the buffer to `1`
- stopping the macro saves `demo` at `1 step`

## Trust impact

This is a trust-first cleanup. Recorded automation should reflect actions that actually ran, not actions that were refused.
