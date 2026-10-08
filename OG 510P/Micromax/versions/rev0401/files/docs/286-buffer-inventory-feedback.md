# Rev344: plain buffer inventory should be legible

This is a tiny trust/flow follow-up to the recent explicit-orientation work.

## Problem

The editor already had good *movement* feedback around buffers:

- `buffer ...` said where it landed
- `bufferpick` said where it landed
- `prevbuf`, `close`, `only`, and `closeall` said which buffer became active next

But the plain `buffers` command still flattened open state to raw names.

That made a very ordinary inspection path weaker than the editor's newer picker and navigation paths:

- the active buffer was only implied
- dirty state was invisible
- readonly state was invisible
- current cursor locations were invisible

For humans this creates unnecessary guesswork.
For future LLMs it also throws away useful state that the repo already knows.

## Change

`buffers` now reports each open buffer as a small inspectable entry:

- active buffer gets a `*` prefix
- `dirty` and `readonly` show up as visible flags
- each entry includes the current cursor target as `@ line:col`

Example shape:

`buffers: 2 buffer(s), alpha [dirty, readonly] @ 2:0; *beta @ 1:2`

## Why this matters

This is not a flashy feature.
It is a small coherence fix.

The editor already had a trustworthy searchable picker and better movement messages.
The plain inventory path should not be a lower-fidelity dialect than those richer surfaces.

A good rule here is:

> ordinary inventory should be legible, not lossy.

That helps both people and tooling answer simple questions quickly:

- which buffer is active?
- which buffers are risky to close?
- which buffers are protected/read-only?
- where was I in each one?

## Scope discipline

This intentionally does **not** try to become a full tab bar, project browser, or multi-pane UI.
It is just a better plain-text inventory message for an already-existing command.

That keeps the change aligned with the current sequencing:

1. trust first
2. taste second
3. flow third

The work is small, obvious, and easy to verify.
