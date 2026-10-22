# Specimen flow 02 — snapshot resume and freshness reacquire

This specimen exists because restored-state systems are a common place where designers overclaim continuity.

## Flow sketch

### 1. A reviewed snapshot or warm template exists
The system begins with a package/bundle and a reviewed resume class. That says something about eligibility to restore, but not yet about present freshness.

### 2. Restore creates a live instance on a particular ground
The restore step yields:
- a concrete ground,
- a live instance,
- and a continuity class such as resumed, recreated-from-template, or fresh-realized.

### 3. Foundry exports a generation witness
The live instance emits a **generation witness** or equivalent continuity marker stating that a new runtime generation exists. This is not a verdict; it is a continuity fact.

### 4. Resume humility is applied
The system marks which facts may no longer be safely inherited from the pre-snapshot world, such as:
- unique IDs,
- secrets or credentials that should be reacquired,
- live network assumptions,
- or freshness-bound attestation material.

This is the **resume humility card**.

### 5. Optional freshness reacquire occurs
If trust-sensitive operations depend on fresh evidence, the instance or its owner requests reacquire. That material belongs to Ward for appraisal.

## What this specimen is testing
- Can Foundry name continuity classes without pretending every restore is a live continuation?
- Can package, reviewed resume class, concrete ground, and live instance stay separate in one flow?
- Can Foundry export the right continuity facts to Ward without swallowing trust policy itself?

## Non-decisions preserved
- no universal resumed-instance truth object;
- no assumption that every snapshot-capable ground shares one continuity model;
- no promise that restore and cold start are interchangeable;
- no forced choice of one preferred substrate family.
