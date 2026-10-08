# Remedy-hardening-attestation closure-proof contract sheet page — governed audience, residual carriers, and proof ceiling

## Purpose

This contract sheet exists so the archive can say exactly what closure claim is being attempted after containment.
It should prevent the operator from silently collapsing `future access blocked` into `audience closed`.

## Required sections

The page must render the same sections in the same order:

1. **Governed audience boundary**
2. **Residual carrier inventory**
3. **Closure horizon and evidence plan**
4. **Strongest honest closure sentence**

### 1) Governed audience boundary

This section must show:

- named audience slices in scope
- which slices are linked devices
- which slices are remote unlinked peers
- which slices are single-file recipients
- which slices are public or forwarded unknowns
- which slices are downstream dependents rather than direct holders

The operator must be able to answer: **who exactly are we trying to close?**

### 2) Residual carrier inventory

This section must list every stale-carrier class that may survive, including at least:

- still-synced folders
- disconnected-but-local folders
- linked-device removed copies
- unlinked remote copies
- single-file downloaded copies
- forwarded or reshared copies
- local-share attachments
- archive or hidden local residue
- screenshots, exports, or non-sync public artifacts if applicable

The operator must be able to answer: **what stale carriers may still exist even after containment?**

### 3) Closure horizon and evidence plan

This section must show:

- closure horizon length
- required confirmations per audience slice
- evidence classes allowed to count toward closure
- evidence classes that are informative but insufficient
- unknown-survivor budget
- automatic invalidators for the closure claim

The operator must be able to answer: **what proof would be enough, and what would still leave closure blocked?**

### 4) Strongest honest closure sentence

This section must preserve two separate sentences:

- strongest honest closure sentence now
- blocked stronger closure sentence

Examples:

- `future joins blocked, survivor set still partly unknown`
- `linked devices closed, remote unlinked closure unproven`
- `named recipients confirmed closed, forwarded copies still possible`
- `audience-wide closure not yet provable`

## Hard rules

The page must never:

- collapse link expiry into recipient cleanup
- collapse linked-device removal into unlinked-peer closure
- omit unknown or unconfirmed survivor slices
- emit `closed` without naming closure scope
