# Overlap lineage receipt page — subject boundaries, bridge paths, and blocked stronger sentences

## Purpose

Emit a durable receipt whenever nested overlap is created, accepted, changed, or retired.

This page exists to answer later:

- `what exact overlap topology was accepted?`
- `which bridge assumptions were relied on?`
- `what stronger belief was explicitly blocked?`

## Required receipt fields

### 1. Receipt header

Must show:

- receipt id
- timestamp
- parent subject id
- child subject id
- overlap path
- originating action (`create overlap`, `accept overlap`, `retire overlap`, `bridge proof update`, `other`)

### 2. Topology summary

Must show:

- whether the child was fully nested inside the parent
- bridge host set at issuance time
- direct seed horizons
- carried-edit horizons

### 3. Cost / posture summary

Must show:

- duplicate indexing / rescan risk accepted or rejected
- whether selective / placeholder incompatibility was relevant
- current budget verdict

### 4. Claim ceiling summary

Must show:

- strongest safe sentence
- blocked stronger sentence
- invalidators

### 5. Successor conditions

Must show:

- what would force rereview
- what bridge-loss event collapses the claim
- whether a detach / flatten successor path was recommended
