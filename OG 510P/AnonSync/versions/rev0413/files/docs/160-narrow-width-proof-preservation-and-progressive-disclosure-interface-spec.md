# Narrow-width proof preservation and progressive disclosure interface spec

## Purpose

Many of the archive's hardest promises are semantic, not visual:

- show current source truth
- show scope truth
- show future-effect truth
- show blocker truth
- show apply consequence truth

Those promises become easiest to break when width is tight.
This document answers the question:

> how should AnonSync compress layout without compressing meaning?

## Core decision

Narrow-width, dense-table, and mobile-like layouts may use stronger progressive disclosure.
They may **not** use progressive disclosure as an excuse to hide load-bearing proof.

The rendering may change.
The semantic minimum may not.

## The non-negotiable payload

Every compressed rendering of a proof-bearing row, card, or draft must preserve access to:

- current source / provenance
- scope class
- strongest honest current answer
- blocker or risk reason, if any
- future-effect summary
- apply or receipt consequence, if action is in scope

If any of those disappear entirely, the layout has become dishonest.

## Compression order

The product should shed information in this order:

1. ornamental chrome
2. secondary history
3. non-load-bearing labels that can be inferred nearby
4. dense examples or long evidence lists
5. only then optional extended explanation

It should not first shed provenance, blocker reason, or future effect.

## Row and card rules

### Effective-value rows

A narrow value row must still show, in compressed form:

- current value
- source (`baseline`, `pin`, `override`, `exception`, etc.)
- future-follow behavior
- edit entry point

A raw value without source is not acceptable.

### Review cards

A narrow review card must still show:

- why this item is in `Now`, `Soon`, or `Quiet`
- the strongest recommended next action
- whether dismissal or snooze changes only presentation
- the main blocker or expiry reason

### Draft summaries

A narrow draft summary must still show:

- subject count
- scope class
- outlier presence
- predicted aftermath class
- whether apply is currently blocked, partial, or ready

### Commit barriers

A narrow commit barrier must still preserve the five core questions:

- what changes now
- what does not change
- what becomes harder to undo
- what appears afterward
- what continuity claim will be made

These may stack vertically, but they may not disappear.

## Progressive disclosure rules

### Allowed

- tap-to-expand proof drawer
- stepper sheets
- accordion sections
- chips that expand into short causal summaries
- split between compact current answer and full explanation pane

### Not allowed

- icons with hidden meaning and no text fallback
- action bars detached from blocker reason
- compressed layouts that show `Apply` before showing scope/consequence
- future-effect text omitted on the theory that the operator can infer it

## Dense table rules

Tables may compress columns aggressively.
But each row must still expose an expansion path that reveals:

- source / provenance
- scope
- blocker / risk
- future effect
- action consequence

The row expansion path should be one step away, not a navigation maze.

## Touch and keyboard parity

A narrow surface may rely more heavily on taps and stacked sheets.
A textual surface may rely more heavily on focus and detail panes.
Both must still make the same proof payload reachable without hidden semantics.

## Result

A good narrow-width rule prevents four regressions:

- provenance becoming decorative instead of operative
- `Apply` floating free from its real consequence
- blocker reasons hiding behind status dots
- future behavior becoming something the operator is expected to remember rather than see

If a layout becomes simpler by dropping the very facts that make a decision safe, it is not a simplification.
It is a semantic regression.
