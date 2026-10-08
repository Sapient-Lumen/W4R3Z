# Adopt, rebind, reconnect, and pre-existing path repair interface spec

## Purpose

Current sync products often teach path continuity through ritual:

- disconnect
- reconnect
- accept a new default path
- notice a duplicate later
- manually hunt back toward the intended directory
- maybe remove and re-add if the state still feels wrong

AnonSync should not do that.

This document decides what interface object answers the real question:

> when a share is visible again or a target path already exists, how should the product compare remembered intent, current bytes, and duplicate risk before claiming continuity?

## Core decision

`Adopt`, `rebind`, `reconnect`, and `repair path` belong to one workflow family.
They all ask variants of the same question:

- what local path relationship is being proposed
- what was previously intended
- what exists there now
- what continuity claim can honestly be made

The interface should therefore use one **path continuity review** object rather than separate magical affordances.

## The four common entry cases

### 1) First adoption of visible incoming state

The share is visible here, but not yet bound locally.

### 2) Reconnect of a previously bound subject

The share was bound here before, but local continuity has been released or paused.

### 3) Rebind to a different target path

The operator intentionally wants a new target path.

### 4) Repair of an intended path that already contains bytes

A target path exists and is not empty, so continuity must be argued rather than assumed.

These are different triggers but one semantic family.

## Path continuity review anatomy

### 1) Subject and continuity header

Show:

- subject label and stable handle
- acting seat
- continuity class (`first-adopt`, `reconnect`, `rebind`, `repair`)
- strongest remembered path, if any
- current proposed path

This is the answer to `what continuity question am I solving right now?`

### 2) Remembered path evidence

If the product knows a prior path, it should say why that memory exists:

- last bound path on this seat
- prior approved repair receipt
- remembered path from same subject lineage
- imported continuity hint from replacement workflow

The product must not treat weak guesses like strong memory.

### 3) Current target inspection

Before bind, inspect the current proposed path and classify:

- missing / empty
- present and empty
- present with matching lineage evidence
- present with partial similarity but unresolved differences
- present with conflicting material
- present with likely duplicate namespace risk
- inaccessible or policy-blocked

### 4) Comparison summary

This section must compare:

- remembered path vs proposed path
- proposed path vs currently observed bytes
- current bytes vs subject identity/lineage evidence

The point is not to compute a false certainty score.
The point is to make the product's best honest claim legible.

### 5) Honest continuity claim

The review should classify the strongest safe statement, for example:

- `Fresh local bind; no prior continuity claim`
- `Rebind to remembered path with strong continuity evidence`
- `Candidate path matches prior location but current bytes need merge review`
- `New path would create a duplicate namespace beside remembered path`
- `Repair blocked until current conflicting bytes are classified`

### 6) Recommended next actions

The primary recommendation should depend on the continuity claim:

- `Bind here`
- `Repair at remembered path`
- `Compare conflicting bytes`
- `Choose different path`
- `Split into merge or preserve-first workflow`
- `Leave visible only`

The primary action should be the safest truthful next step, not the fastest namespace creation.

## Duplicate-risk rules

The product should treat duplicate-risk as a first-class proof-bearing condition.
Indicators may include:

- same subject name at different nearby paths
- remembered path differs but proposed path would create sibling duplicate
- existing target contains bytes from older or divergent lineage
- disconnected state plus automatic new default path
- same seat recently bound this subject elsewhere

Duplicate-risk should never be hidden behind a bland `folder already exists` prompt.

## Empty vs non-empty targets

### Empty target

Empty target is the easiest case.
The workflow may stay compact.

### Non-empty target

Non-empty target always deserves stronger review.
At minimum the product should classify whether the bytes are:

- unrelated
- partially similar
- likely intended continuation
- likely duplicate copy
- conflicting mixed material

Blind `add anyway` is not good enough.

## Reconnect rules

Reconnect must not default to `create a new folder and let the operator sort it out later`.
If a remembered path exists, the workflow should normally begin there.
If another path is proposed instead, the product should explain why.

Reconnect is therefore a continuity workflow, not a default-location workflow.

## Repair vs replace-new rules

Sometimes continuity should not be restored.
The operator may intentionally want a fresh local copy at a new path.
That is fine.
But the product should classify this as:

- `new local bind beside prior continuity`
- not `reconnect succeeded`

This vocabulary matters because the receipts should tell the truth later.

## Dense and narrow surfaces

Dense surfaces may collapse detailed path comparison into expandable rows.
They may not omit:

- remembered path
- proposed path
- duplicate-risk class
- strongest honest continuity claim

## Result

A good path continuity review prevents five common mistakes:

- reconnect silently creating a duplicate namespace
- a remembered intended path disappearing behind a new default path suggestion
- non-empty target bytes being treated as harmless without comparison
- operators thinking `bind succeeded` means `continuity restored`
- repair work degenerating into remove-and-re-add ritual

If the product solves reconnect by proposing a new folder first and explaining continuity later, it has already taken the wrong interface path.
