# Crate lifecycle-surface barrier boundaries — 2026-03-20

This note keeps **P-0520 Crate Lifecycle Surface Pack Kit** from collapsing shutdown-barrier truth into generic “graceful shutdown support”.

## The sharper seam

Within **P-0520**, keep these claims separate:

1. **a stop signal exists**,
2. **a stop verb was invoked**,
3. **a shutdown barrier completed**,
4. **some work escaped that barrier**,
5. **some dependency blocked that barrier**,
6. **cleanup evidence proved a stronger level of completion**.

Those are related, but they are not the same product claim.

## What belongs in the shutdown-barrier seam

The barrier seam is about questions like:

- What event actually counts as shutdown completion?
- Does completion mean the listener stopped, the tracked task set is closed-and-empty, or the full protocol-facing work drained?
- Which tasks or components are outside that barrier?
- Which components can keep the barrier pending?
- Which stop routes must be composed to make the user-facing stop story true?

## What it is not

### 1. Not generic stop semantics

`drop`, `abort`, `cancel`, `close`, `shutdown`, `join`, and `detach` are stop verbs.
Barrier truth asks what combination of those verbs and waits actually counts as **completion**.

### 2. Not just background-work discovery

A background-work map can say that some task exists.
Barrier truth asks whether that task is **inside or outside** the completion story.

### 3. Not just drain recipes

A drain recipe tells a user what to do.
Barrier truth tells them **what the recipe buys** and what still escapes it.

### 4. Not observability or diagnosis support

Telemetry and diagnosis lanes may observe stuck shutdowns.
The barrier seam is the receiver-facing contract for what shutdown completion is supposed to mean in the first place.

### 5. Not framework-specific bug triage

Framework issues are useful evidence.
But **P-0520** should stay a cross-crate contract layer above any one framework’s current issue queue.

## Working rule for future passes

When a future pass sharpens **P-0520**, it must say explicitly whether it is adding:

1. **activation-boundary truth**,
2. **stop-semantics truth**,
3. **shutdown-barrier truth**,
4. **escape-path truth**,
5. **blocking-work caveats**,
6. **teardown evidence**,
7. or **drain-recipe guidance**.

Do **not** let the archive quietly rephrase barrier truth as “better graceful shutdown docs”, “better task tracking”, or “another cancellation helper”.
