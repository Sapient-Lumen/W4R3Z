# Parse lenses, diagnostic rails, and packet gutters

The future ViewFS shell should feel fast and rich **without** pretending every bright piece of UI is already an action.

## The ladder

One line should be able to move through visibly different stages:
- **editable buffer** — just what is currently being typed/edited
- **parse lens** — best current structural understanding
- **diagnostic rail** — syntax/lint/hint/advice about the current buffer
- **packet gutter** — current pane-local compile/bind result
- **prepared-action shutter** — exact act that is now reviewable/launchable
- **receipt ghost** — only history

## Parse lenses

A parse lens should be able to show:
- segment boundaries,
- pipeline/group structure,
- quoted versus literal regions,
- object-token versus plain-text posture,
- recovery state when the buffer is incomplete.

This is where the shell becomes super awesome without becoming dishonest.
Users get immediate structure and navigability before the line is even done.

## Recovery veils

When the parser is guessing through incomplete text, the shell should say so.
Useful postures include:
- `partial parse`
- `recovered parse`
- `ambiguous split`
- `binding postponed`

That is much better than red/green theater.

## Diagnostic rails

Diagnostics should stack by kind instead of flattening into one red underline:
- `syntax`
- `lint`
- `hint`
- `policy advice`
- `history note`

A diagnostic rail should explain:
- where it came from,
- whether it is purely advisory,
- whether it was computed from the buffer only or from current pane-local bindings,
- whether it is stale/history-only.

## Packet gutters

A packet gutter should appear only after compile/bind has happened against the current pane.
It should be able to say:
- `compiled from current buffer`
- `uses current pane handle H7`
- `route slip embedded`
- `portal needed`
- `rebind needed`
- `ready for review`

That keeps buffer truth separate from packet truth.

## Great steals for the custom shell+terminal

- **cursor-near parse cards** that explain the current token/segment without opening a giant inspector.
- **recovery fog** over uncertain regions instead of fake exactness.
- **diagnostic rails** in the gutter with source badges like `parser`, `lint`, `policy advice`, `history`.
- **packet gutters** that only materialize once current objects/receipts have actually been bound.
- **compile diff cards** when the same visible buffer compiles differently because pane-local bindings changed.

## Product posture

The shell should feel like:
- an editor while you are editing,
- an analyzer while it is explaining,
- a router when it has compiled a packet,
- and a launcher only after preflight/review.

That separation is exactly what will let ViewFS stay capability-honest while still feeling dramatically better than a traditional shell.
