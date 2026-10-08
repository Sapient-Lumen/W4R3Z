# Remedy-hardening-attestation successor action-envelope proof page — preflight diff, expected effects, and runtime ceiling

## Purpose

This page is the durable proof artifact for a reviewed execution envelope.
It preserves what the product believed would happen before the action started, which guardrails were armed, which hazards remained, and which stronger containment sentence therefore stayed blocked.

## Minimum proof bundle

The proof page must preserve at least:

- source action-plan receipt identifier
- source authorization receipt identifier
- envelope review identifier
- preflight timestamp
- reviewer identity or reviewer set
- predicted touched-set snapshot
- predicted counts by dimension
- predicted permission and approval effects
- predicted hydration effects
- predicted reconnect or rescan effects
- explicit out-of-envelope exclusions
- armed trip conditions
- brake availability assessment
- fail-closed versus fail-open classification
- runtime watcher set
- unresolved unknowns at arm time
- strongest safe sentence at arm time
- strongest blocked stronger sentence at arm time

## Proof sections

### 1. Preflight diff

Show a compact diff between:

- current world state before arm
- expected world state if execution stays within envelope
- forbidden changes that would constitute a trip

### 2. Side-effect ledger

List expected side-effects in typed buckets:

- bytes hydrated
- paths created or rebound
- peers admitted
- approvals reused
- permissions escalated or reduced
- deletes propagated
- scans or rescans expected
- reconnect channels still armed

### 3. Guardrail ledger

For each guardrail show:

- what it watches
- exact trip condition
- automatic or manual response
- what it cannot prevent
- which stronger sentence it does **not** justify by itself

### 4. Runtime ceiling statement

The page must end with a bounded ceiling such as:

- `reviewed envelope only; within-envelope execution not yet observed`
- `hard trip guards armed; fail-closed only for named dimensions`
- `manual abort available; fail-open residue still possible`
- `placeholder-only preview safe; full hydration path blocked`
- `remembered-approval spillover unresolved; stronger containment sentence blocked`

## Evidence grading

The proof page must support at least these grades:

- plan-only, no runtime-envelope proof
- preflight preview only
- preflight plus guardrails armed
- preflight plus hard-stop verified in test
- preflight plus live run observed within envelope for named slice
- preflight contradicted by live overspill
- proof invalidated by later hazard discovery

## Hard rules

The page must never:

- collapse a predicted touched-set into a guaranteed touched-set
- treat a soft warning as a hard-stop
- treat pause as if it stops all relevant side-effects
- erase the unknown remainder from the preflight record
- replace a blocked stronger sentence with optimistic prose after execution starts
