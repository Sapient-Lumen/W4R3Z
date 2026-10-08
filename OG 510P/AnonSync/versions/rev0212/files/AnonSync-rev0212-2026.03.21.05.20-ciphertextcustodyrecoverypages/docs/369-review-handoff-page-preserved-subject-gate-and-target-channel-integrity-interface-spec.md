# Review handoff page: preserved subject, gate, and target-channel integrity interface spec

## Purpose

The archive already had cross-channel parity doctrine.
This document makes the handoff page concrete.

The page exists to answer one ordinary operator question:

> if this work has to move to another channel, what exactly is being preserved, what might reopen, and what target channel is honest for this action?

## Core decision

Every non-trivial cross-channel continuation must compile to one first-class **Review handoff** page.
That page is the semantic home of:

- preserved action identity
- preserved subject/draft/gate context
- target-channel choice
- integrity and parity rules
- receipt promise
- expiry and consumption state

The product must not treat `continue in CLI` or `open desktop app` as a naked jump.

## Primary page layout

The page always renders the same top-level regions in the same order:

1. handoff strip
2. preserved-action card
3. target-channel chooser
4. parity-and-reopen card
5. apply-continuity promise
6. handoff receipt preview
7. existing handoff ledger

### 1) Handoff strip

Show:

- action family
- subject
- source channel
- why handoff is needed
- strongest recommended target channel

### 2) Preserved-action card

Show the context that is expected to survive:

- subject reference
- review family
- draft or plan handle when present
- mutation gate or capability reference when present
- blocker context already established
- sections already completed

This card should answer `what reviewed work have I already done that should not be lost?`

### 3) Target-channel chooser

Each target row should show:

- channel kind (`local-web`, `desktop`, `cli`, `tui`, `api-backed`, `other`)
- current readiness
- whether apply is possible there
- trust/auth requirements
- whether it preserves the current gate and draft exactly

The page should be able to recommend a target without pretending only one target exists.

### 4) Parity-and-reopen card

Show:

- which review sections are guaranteed to survive unchanged
- which facts would force broader review to reopen
- whether the target channel is fully equivalent, inspect-only, or apply-capable with narrower limits
- whether any channel-specific degradation still remains after handoff

This card should answer `am I moving the same reviewed action, or only part of it?`

### 5) Apply-continuity promise

Before the handoff is created, show:

- whether the target can apply directly or only continue inspection
- whether new trust/session work is required first
- whether the gate will be revalidated on arrival
- whether the action expires if not resumed soon

### 6) Handoff receipt preview

Show the receipt that will be emitted, including:

- source channel
- target channel
- preserved subject and review family
- gate continuity state
- expiry time
- whether the handoff was later continued, reopened, refused, or expired

### 7) Existing handoff ledger

Show current and recent handoffs with:

- action family
- source and target
- state (`ready`, `continued`, `reopened`, `expired`, `consumed with apply`)
- preserved-versus-reopened verdict
- actor and timestamp

## Narrow-width behavior

In narrow width the page may compress the chooser, but it may not hide:

- why handoff is needed
- preserved subject/draft/gate truth
- whether the target preserves apply or only inspection
- expiry and receipt promise

## Acceptance criteria

This spec is satisfied when:

- channel switching does not become a semantic blind jump
- the operator can tell what survives and what may reopen before leaving the source channel
- the handoff itself becomes a durable object with expiry and receipt state
- target-channel choice stays explicit rather than hidden behind one preferred button
