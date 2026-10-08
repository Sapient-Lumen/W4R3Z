# Hydration evidence page: engine proof, lane health, and history/collision witness interface spec

## Purpose

This page exists because later operators need proof, not lore.
If the product says a seat is using a certain hydration engine, supports shell-open downloads, or has a narrower history/collision contract, the evidence has to be inspectable.

## Evidence families

The page should group evidence into four families:

1. **Engine proof**
2. **Lane health proof**
3. **Eligibility proof**
4. **Guarantee proof**

### 1) Engine proof

Show:

- current engine kind
- policy source and policy epoch
- provider/API basis if the engine depends on one
- whether the engine is native, fallback, or inferred from degraded state

### 2) Lane health proof

Show:

- shell/provider extension status
- in-app fallback status
- latest successful open/materialize/evict action per lane
- recurring missing-action or disappearing-menu observations

### 3) Eligibility proof

Show:

- current OS / provider version basis if relevant
- filesystem / path class
- whether the path is local, mounted, or provider-managed
- co-tenant provider / runtime detections
- inherited flags or attributes that may override expected defaults

### 4) Guarantee proof

Show:

- current retained-history class
- current collision-detection class
- evidence run or policy source that established those classes
- examples where the engine narrowed history, delete handling, or conflict proof

## Detailed surface

### Table A — Seat evidence

Columns:

- seat
- engine kind
- lane health
- eligibility verdict
- history guarantee
- collision guarantee
- evidence freshness

### Table B — Path findings

Columns:

- path sample
- path class
- engine eligibility
- co-tenant finding
- inherited-flag finding
- strongest resulting ceiling

### Table C — Action witness samples

Columns:

- action sample
- lane used
- outcome
- history effect
- collision effect
- timestamp

## Safe claims this page should enable

- `This seat uses an OS hydration engine on an eligible local path; shell-open and in-app fetch are both healthy.`
- `This seat fell back to in-app-only hydration because provider integration is degraded.`
- `Rollback is delete-only under the active hydration engine on this seat.`
- `Collision detection is narrowed under the current engine; treat local edit conflicts as lower-confidence.`
- `A competing cloud-file provider already occupies this path class, so the stronger engine is blocked.`

## Rules

### Rule 1 — proof must separate engine kind from lane health

A degraded lane does not necessarily mean the wrong engine.
The page must keep those apart.

### Rule 2 — guarantee proof must cite the reason for narrowing

A narrowed history/collision claim must state whether the cause is engine kind, version line, path class, or co-tenant state.

### Rule 3 — inherited local flags are evidence, not folklore

If a provider/API leaves local flags that alter expected hydration behavior, the page must publish them.

## Acceptance criteria

A later operator can:

- verify which hydration engine was active
- verify which local lanes were healthy or degraded
- verify why a path was eligible or blocked
- verify whether rollback and collision claims were narrowed
- distinguish proven ceilings from speculation
