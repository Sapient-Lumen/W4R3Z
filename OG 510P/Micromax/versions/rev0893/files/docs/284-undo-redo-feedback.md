# Undo/redo feedback (rev342)

Rev342 tightens a small trust-first gap in ordinary edit recovery.

The editor already had the important substrate:

- a real linear undo/redo stack
- grouped scripted edits through `ed.with-undo`
- useful internal edit descriptions such as `insert 3`, `replace`, `paste`, `delete`, and `qreplace`

But the *user-facing* recovery loop still lagged behind the rest of the repo's recent honesty/orientation work.

## What felt wrong before

`Undo` / `Redo` usually changed the buffer correctly, but the loop itself stayed too quiet.

That meant:

- key-driven recovery could mutate text without saying what just happened
- command-bar mirrors did not exist, so the recovery loop was less discoverable than nearby navigation loops like `jumpback`, `helpback`, or `buffer`
- empty-stack retries could fail without a tiny explicit explanation

In a visible TUI, users can sometimes reconstruct what changed by staring at the screen. In headless tests, scripted usage, or future LLM-guided sessions, that is unnecessary ambiguity.

## What changed

Rev342 keeps the implementation deliberately small:

- undo records now carry a tiny target label helper
- key-driven `Undo` / `Redo` now report the traversed edit description plus the touched target
- command-bar `undo` / `redo` now mirror the same behavior
- empty-stack retries now fail explicitly

Examples:

- `undo: insert 3 -> *t* @ 1:0`
- `redo: insert 3 -> *t* @ 1:3`
- `undo: nothing to undo`
- `redo: nothing to redo`

## Why this matters

This is a trust change, not a new subsystem.

The repo has recently been making ordinary movement and automation loops tell the truth about what they actually did:

- open/save/replace feedback
- buffer/jump/help/search/jumphistory orientation
- mark placement visibility
- macro playback and macro inventory honesty

Undo/redo belongs in that same family. Recovery should feel as inspectable as navigation.

## What this is not

This is intentionally **not**:

- an undo tree
- a visual history browser
- multi-buffer transactional history
- aggressive undo coalescing policy work

Those may still be worth exploring later. Rev342 is the smaller prerequisite: when the user asks the editor to recover from an edit, the editor should say what recovery step it just traversed.
