# RATE-ERROR-BOUND-TEST

This note tries to break the archive's new Lane A field candidate.

## Question

Can `rate_error_bound` really carry Lane A pressure by itself,
or does Lane A actually force a second semantic such as explicit stability class or holdover confidence?

## Current result

`rate_error_bound` survives **provisionally**.

But it only survives in a narrower form:
- bound over the **current validity window**
- interpreted under the **current regime**
- and read alongside existing `freshness` and `holdover_class` semantics

## Why the simple version failed

### 1. Offset and stability are not the same thing
A single naked rate number would blur together concerns that the source base keeps distinct.
That is not honest enough.

### 2. Holdover changes the meaning of the claim over time
A rate claim that is acceptable just after reference loss is not equally trustworthy much later into holdover.
That means the bound has to be windowed, not timeless.

### 3. Residual frequency error exists even in controlled loops
The source base keeps showing that the system can remain disciplined while still carrying residual error.
That pushes the field toward an uncertainty-style meaning rather than a simple reading.

## Why the candidate still survives

### 1. The archive already has neighboring semantics
The current state shape already includes:
- `freshness`
- `regime`
- `holdover_class`

That means `rate_error_bound` does not need to carry the entire burden alone.

### 2. Lane A still wants a bounded external statement
Even after the break attempt, a binary label or a raw offset value still looks too weak.
Lane A pressure still points toward a bounded claim.

## Revised reading

The archive should read `rate_error_bound` as:

> the currently claimable bound on rate error relative to the reference, over the current validity window, under the current regime

That is narrower and more honest than the previous reading.

## What would still break it

The archive should abandon or split this field if:
- Lane A consumers need both a bound and an independent first-class stability semantic
- the meaning changes too much across holdover stages to stay compact
- the archive finds that downstream users really need decomposed drift / stability / continuity semantics rather than one bounded claim

## Current archive posture

Keep `rate_error_bound`, but only as a **windowed** bound with explicit dependence on existing state and hook context.
