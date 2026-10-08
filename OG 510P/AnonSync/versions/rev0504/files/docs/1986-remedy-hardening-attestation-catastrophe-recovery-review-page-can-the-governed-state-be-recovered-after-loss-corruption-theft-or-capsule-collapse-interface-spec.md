# Remedy-hardening-attestation catastrophe-recovery review page — can the governed state be recovered after loss, corruption, theft, or capsule collapse?

## Purpose

This page is the operator-facing review that answers the practical catastrophe question after steady-state durability and named regime-shift robustness are already good enough: given that the target state used to be true, can it still be recovered after a destructive event without lying about whether the same governed world survived?

## Primary review prompts

The review must answer these prompts in order:

1. **Which durable or regime-shift receipt is the starting basis for this catastrophe review?**
2. **What exact catastrophe is under review: corruption, storage loss, stolen device, `.sync` capsule loss, unsupported clone restore, key loss, or world reset?**
3. **Which anchors survived: bytes, databases, keys, identity, `.sync` capsule, receipts, storage root, control records?**
4. **Which parts must be regenerated, re-added, relinked, reshared, or re-founded?**
5. **Does the proposed recovery preserve the same world, or does it create a successor world that only inherits some bytes or policy?**
6. **What is the strongest catastrophe-recovery sentence the product may honestly publish now?**

## Review sections

### 1. Pre-catastrophe basis board

Show:

- source durable or regime-shift receipt
- target sentence before catastrophe
- governed slice
- strongest honest sentence before failure

### 2. Catastrophe-class board

Show:

- catastrophe class under review
- whether the event destroyed bytes, anchors, identity, or only control capsule state
- whether a supported recovery path exists
- whether recovery depends on pre-saved anchors

### 3. Anchor-retention board

Show:

- bytes retention
- database-lineage retention
- key or secret retention
- identity retention
- `.sync` capsule retention
- storage-root retention
- receipt and proof retention

### 4. Re-foundation and regeneration board

Show:

- whether Sync instance must be re-added
- whether identity must be regenerated
- whether folders must be reshared or reconnected
- whether the resulting world is same-world recovery or successor-world re-foundation

### 5. Recovery sentence chooser

The review must output one and only one primary sentence class such as:

- catastrophe unreviewed
- bytes salvage only, continuity unknown
- anchor-dependent recovery possible
- encrypted-backup path conditional on retained keys and database lineage
- `.sync` loss repaired by creating new synchronization instance
- stolen-device response requires successor-world re-foundation
- named catastrophe recovered for named slice only
- same-world reconstitution proven for named slice only
- broader all-catastrophe recovery robustness blocked

## Hard rules

The review must never let an operator hide:

- regenerated identity behind `recovered`
- a new synchronization instance behind `same share restored`
- restored bytes behind `full continuity`
- unsupported clone restoration behind `rebuild succeeded`
- missing anchor retention behind `probably recoverable`
