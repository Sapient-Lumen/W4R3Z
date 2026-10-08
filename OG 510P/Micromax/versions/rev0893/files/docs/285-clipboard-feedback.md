# Clipboard feedback (rev343)

Rev343 tightens a small trust/flow gap in the ordinary clipboard loop.

The editor already had the important substrate:

- a real internal clipboard with item-wise and linewise kinds
- multicursor-aware `Copy` / `Cut` / `Paste`
- smartpaste for small indentation-friendly multiline inserts
- best-effort external clipboard import/export paths when configured

But the *user-facing* clipboard loop still lagged behind the repo's recent honesty/orientation work.

## What felt wrong before

Clipboard actions mostly worked, but they still spoke too vaguely.

That meant:

- `Copy` and `Cut` ended with one-word acknowledgements that hid how much text actually moved
- successful `Paste` mutated text without saying what got inserted or where the primary cursor landed
- an empty internal clipboard could still make `Paste` fail silently

In a visible TUI, users can sometimes reconstruct this by staring at the screen. In headless tests, scripted usage, or future LLM-guided sessions, that is unnecessary ambiguity.

## What changed

Rev343 keeps the implementation deliberately small:

- `Copy` now reports selection count plus copied-char total
- `Cut` now reports selection count plus copied-char total and the landed target
- successful `Paste` now reports cursor count, inserted chars, and the landed target
- empty internal-clipboard paste now fails explicitly

Examples:

- `copied: 1 selection, 5 chars`
- `cut: 2 selections, 6 chars -> *t* @ 1:0`
- `paste: 1 cursor, 5 chars -> *t* @ 1:16`
- `paste: clipboard empty`

## Why this matters

This is a trust/flow change, not a new clipboard subsystem.

The repo has recently been making ordinary movement and recovery loops tell the truth about what they actually did:

- open/save/replace feedback
- buffer/jump/help/search/jumphistory orientation
- mark placement visibility
- undo/redo recovery honesty
- macro playback and macro inventory honesty

Clipboard actions belong in that same family. Small text movement should feel inspectable, not tacit.

## What this is not

This is intentionally **not**:

- a kill-ring redesign
- richer clipboard history browsing
- system clipboard policy expansion
- new paste transforms beyond the existing smartpaste path

Those may still be worth exploring later. Rev343 is the smaller prerequisite: when the user asks the editor to move text through the clipboard, the editor should say what moved.
