# Reclaim receipt page: postcondition, byte delta, and preservation proof interface spec

## Purpose

This page answers:

> what actually changed after reclaim, which byte classes really shrank, which intended truths were preserved or weakened, and what residue or follow-on checks remain?

The page exists because `cleanup complete` is not a trustworthy postcondition.

## Core rule

Every non-trivial reclaim action must emit one first-class **Reclaim receipt** page after apply.
That page owns:

- observed byte deltas by class
- intended versus observed effect
- preserved truths and weakened truths
- residual bytes still present
- next verification step

## Primary layout

The page always renders the same regions:

1. receipt verdict
2. observed byte-delta card
3. preservation / weakening card
4. residual blockers card
5. lineage and audit card

### 1) Receipt verdict

Show:

- receipt label and timestamp
- action lineage reference
- strongest honest summary
- outcome verdict: `completed`, `completed-with-residue`, `partially-applied`, `blocked-midway`, `verification-incomplete`

### 2) Observed byte-delta card

Show actual observed change by class:

- bytes before
- bytes after
- delta
- observation freshness
- estimation caveats if exact measurement was impossible

Classes should match Byte-class inventory naming so the operator can compare preview and result directly.

### 3) Preservation and weakening card

Show explicitly:

- truths intentionally preserved
- truths intentionally weakened
- truths that unexpectedly changed
- truths still awaiting later proof

Examples:

- `subject membership preserved`
- `restore window shortened`
- `diagnostic residue unchanged`
- `state-root continuity unaffected`
- `later rematerialization depends on surviving full source`

### 4) Residual blockers card

Show:

- pressure still present or resolved
- top remaining byte contributors
- any residual unknown bytes
- whether another reclaim review is recommended
- whether a different family of action is now required instead of more reclaim

### 5) Lineage and audit card

Show:

- parent pressure case
- parent reclaim preview, if any
- seat / subject / state-root scope
- operator or automation actor
- evidence used for postcondition verification

## Honest outputs

This page may conclude:

- `3.4 GiB reclaimed; pressure resolved; history preserved`
- `8.1 GiB reclaimed; restore posture weakened intentionally`
- `partial reclaim applied; diagnostic residue still dominates`
- `verification incomplete; byte classes changed but pressure freshness stale`

It may not collapse these into `cleanup successful`.

## Rules

### Rule 1 — compare intent to outcome directly

The receipt must preserve preview-vs-observed comparison whenever a preview existed.

### Rule 2 — preservation proof matters as much as freed bytes

A reclaim action that freed the intended bytes but silently weakened a stronger truth is not a clean success.
The receipt must say so.

### Rule 3 — residue is not failure by default

Residual bytes or remaining pressure may be an expected result.
Show them as typed residue, not as generic error.

### Rule 4 — audit language must stay operator-readable

Do not force the operator to infer meaning from internal storage paths alone.
Class and consequence must stay primary.

## Event language

Use explicit phrases such as:

- `residual temp bytes reclaimed; payload and archive unchanged`
- `local payload eviction completed; rematerialization remains possible from surviving peers`
- `archive trimmed intentionally; restore posture reduced as reviewed`
- `receipt incomplete because post-action measurement is stale`

Avoid vague lines such as:

- `cleanup done`
- `space optimized`
- `storage refreshed`

## Non-clone reason

Current official Resilio docs explain many ways to free or move bytes, but they do not give one durable product-owned proof page for what exactly changed afterward.
AnonSync should instead expose one Reclaim receipt page where byte delta, preserved truths, and residual blockers remain visible together.
