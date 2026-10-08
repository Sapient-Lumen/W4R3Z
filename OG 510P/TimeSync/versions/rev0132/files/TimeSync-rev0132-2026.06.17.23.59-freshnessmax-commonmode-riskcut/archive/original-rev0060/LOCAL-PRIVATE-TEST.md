# LOCAL-PRIVATE-TEST

This note tests whether the broadest remaining anchor category, `local_private`, should split.

## Question

After reducing the anchor axis into categories,
does `local_private` still hide more than one real anchor family,
or do its current internal differences belong somewhere else?

## Current result

**Do not split it yet.**

The archive can currently keep `local_private` as one category.
The main differences inside it appear to belong to:
- `regime`
- `holdover_class`
- `evidence_posture`

rather than to a second anchor family.

## Why the category looked dangerous

`local_private` currently has to cover things like:
- a local clock in holdover after losing its controlling reference
- a local oscillator with knowledge of past performance
- a private internal timing basis that may persist for longer than an emergency holdover

That is a lot of variation.

## Why the archive still keeps it whole

### 1. Holdover is already a separate semantic family
The source base explicitly treats holdover as an operating condition after a controlling reference is lost.
That means a large part of the variation inside `local_private` is already better modeled by `regime` and `holdover_class`.

### 2. Local-clock capability is not the same thing as a new anchor family
The source base also distinguishes cases where a local clock provides only a timing or frequency solution.
That is important,
but it does not yet force a second private anchor category at the hook level.

### 3. No concrete boundary has yet required the split
The archive still lacks a concrete case where a receiver or interface would behave differently because one `local_private` subtype was used instead of another,
independent of regime or holdover semantics.

## Archive judgment

Keep:
- `local_private`

Do not yet split into things like:
- temporary local holdover anchor
- long-lived private institutional anchor
- sovereign local anchor

Those may become useful later,
but current evidence does not force the distinction at the hook level.

## What this means

The reduced traceability hook is now more stable than it was a few revisions ago.
It appears to survive:
- finance
- synchrophasor / power
- telecom
- local/disconnected pressure

without needing to grow.

## Next useful move

The next best use of this work is not more reduction.
It is to feed the stabilized hook back into the greenfield track and ask what a from-scratch TimeSync design would do differently if it treated this hook as first-class from the beginning.
