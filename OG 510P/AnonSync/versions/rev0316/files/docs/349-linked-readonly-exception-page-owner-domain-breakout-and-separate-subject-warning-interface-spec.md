# Linked read-only exception page: owner-domain breakout and separate-subject warning interface spec

The archive already had readonly-local-write doctrine and authority-mutation doctrine.
What it still lacked was one ordinary page for the question:

> when one seat inside a broadly linked owner family should become read-only, is the product narrowing that seat inside the same governed subject, or is it forcing the operator into a separate lower-governance subject with its own capability artifact and path bind?

Current Resilio docs still make this seam especially clear.
They still say linked devices under one identity act as Owners, and if the operator wants one linked device to be read-only the documented path is to create/use a Standard folder with a Read Only key, disconnect the existing connection, paste the key manually, and choose a path.
That is not an in-place per-seat exception.
It is a side-door separate-subject ritual.

## Page promise

The Linked read-only exception page should make five answers adjacent:

1. requested exception now
2. why same-subject narrowing is or is not available
3. whether a separate subject is being created
4. what path / byte / peer consequences follow
5. strongest honest next action

The page exists so `make this one device read only` stops disguising a class breakout.

## Fixed page order

Every linked-readonly exception page should render the same sections in the same order:

1. **Source subject snapshot**
2. **Requested seat exception**
3. **Same-subject feasibility verdict**
4. **Separate-subject consequences**
5. **Bind and continuity review**
6. **Receipt promise**

### 1) Source subject snapshot

This section should show:

- source subject and current class
- linked seat family currently attached
- current authority model for those linked seats
- whether all linked seats presently inherit broad owner-like power, shared write authority, or something narrower

The operator should be able to answer: **what authority family am I trying to carve an exception inside?**

### 2) Requested seat exception

This section should show:

- target seat
- requested outcome (`readonly observe`, `readonly with local edits ignored`, `readonly with auto-restore`, `serve-but-not-write`, etc.)
- whether the operator expects a simple policy change or is willing to create a derivative subject

The operator should be able to answer: **what exact exception do I want for this one seat?**

### 3) Same-subject feasibility verdict

This section should state clearly:

- `in-place seat narrowing available`
- `in-place seat narrowing unavailable`
- `requested outcome conflicts with current owner-family contract`
- `separate subject / derivative required`

The operator should be able to answer: **can this exception honestly exist inside the current subject at all?**

### 4) Separate-subject consequences

When a breakout is required, this section should show:

- new subject class or derivative class
- new capability artifact family required
- whether the target seat must disconnect from the original attachment first
- whether the resulting seat is no longer a normal linked-owner descendant for this subject
- which future rights, peer grouping, and mutable-grant semantics change with the breakout

The operator should be able to answer: **what am I creating instead of the thing I thought I was toggling?**

### 5) Bind and continuity review

This section should show:

- whether the seat will bind to the same bytes or a different target
- whether the old writable bind must be removed first
- whether pre-existing bytes at the chosen path are being adopted, merged, or risked
- how the target seat will appear in peer views after the breakout

The operator should be able to answer: **what continuity survives this exception, and what family membership story changes?**

### 6) Receipt promise

A linked-readonly exception receipt should preserve:

- source subject
- target seat
- requested exception
- same-subject feasibility verdict
- whether a separate subject/derivative was created
- resulting class / artifact / bind story
- warnings explicitly acknowledged

The operator should be able to answer: **did I narrow one subject, or did I create a side-door replacement for this seat?**

## What this page must never imply

The page must never imply that:

- a per-seat read-only request is always a local toggle
- a seat can remain inside an owner-family subject while silently losing owner-family semantics
- a separate raw-capability subject is merely another view of the original linked subject
- manual key entry and path choice are details rather than evidence of a new subject story
- post-breakout peer rows mean the seat still belongs to the same governance family in the same way

## Result

This page is how AnonSync borrows Resilio's honesty that linked read-only can require a different subject ritual, while refusing the weaker habit of hiding that truth inside an advanced-configuration how-to.
