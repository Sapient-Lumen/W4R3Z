# Derived-rights and lifecycle review page: owner ceiling, source downgrade cascade, and reattach requirement

This page exists so a self-edge derivative cannot pretend it has ordinary-share authority or independent survival.
The derivative inherits from the source, cannot rise above it, and may need destructive ritual to change later.

## Operator question

> What authority does this derivative really have, what source changes will flow down to it, and what must be recreated or manually reattached later?

## When this page must appear

Render whenever the operator:

- creates a derivative with writable or read-only intent
- inspects why a derivative changed rights unexpectedly
- repairs a derivative after source disconnect/removal
- tries to edit derivative rights or resume it after entitlement/source change

## Fixed review order

1. **Source rights and derivative ceiling**
2. **Change ritual**
3. **Source-driven downgrade / removal consequences**
4. **Return and reattach boundary**
5. **Lifecycle receipt promise**

## 1) Source rights and derivative ceiling

Show:

- source access class
- maximum derivative access class
- whether `Owner` is unavailable to the derivative
- whether encrypted-source posture blocks local derivation for this seat
- strongest safe sentence: `inherits source ceiling`, `narrower than source`, `blocked by source rights`, `unknown`

The operator must be able to answer: **how much power can this derivative ever carry?**

## 2) Change ritual

Show:

- whether rights can be changed inline
- whether Advanced-share derivative rights require remove-and-re-share
- whether the current attempt is a live edit, a successor object, or blocked
- expected disruption of the ritual: `none`, `brief`, `full recreate`, `unknown`

The operator must be able to answer: **is this a harmless edit or a re-share boundary?**

## 3) Source-driven downgrade / removal consequences

Show:

- what happens when source rights are lowered remotely
- whether derivative rights auto-lower accordingly
- what happens when source is disconnected
- what happens when source is removed
- derivative survival class: `removed with source`, `frozen`, `detached`, `unknown`

The operator must be able to answer: **what source changes automatically change or destroy the derivative?**

## 4) Return and reattach boundary

Show:

- whether a returning source auto-restores the derivative
- whether manual reattach is required
- whether the operator must create a new derivative entirely
- whether linked same-identity devices ever receive this derivative automatically

The operator must be able to answer: **if the source comes back, what exact manual work still remains?**

## 5) Lifecycle receipt promise

The receipt must preserve:

- source rights at creation time
- derivative ceiling at creation time
- later source-driven downgrade events if observed
- removal / disconnect event that tore down the derivative
- whether resume requires reattach or recreation

## Primary actions

- `Create read-only derivative`
- `Create writable derivative within source ceiling`
- `Re-share derivative with new rights`
- `Resume after manual reattach`
- `Reject because requested rights exceed source ceiling`

## What this page must never imply

It must never imply that these are the same:

- source rights and derivative rights
- source return and derivative return
- inline rights edit and re-share ritual
- local seat continuity and linked-seat propagation
- still listed in UI and actually restorable without manual work

## CLI projection expectation

A text rendering must say, in plain language, whether `Owner` is impossible, whether the derivative auto-lowers on source downgrade, and whether source reappearance still requires manual reattach.
