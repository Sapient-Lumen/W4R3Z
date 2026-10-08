# Footprint review page: counted bytes, placeholders, Archive, and service storage interface spec

## Purpose

This page exists for the ordinary storage dispute:

> the product says one size, the file browser shows another, the disk says something else, and the operator needs a disciplined way to see where the bytes actually live.

## Core decision

AnonSync must expose one **Footprint review** whenever a visible size claim and real occupancy can diverge because of placeholders, ignored subjects, hidden Archive, service storage, or remote-only visibility.

## Review layout

1. **Claim under review**
2. **Counted-scope block**
3. **Occupancy split block**
4. **Residency and cleanup block**
5. **Blocked stronger sentence**

### 1) Claim under review

Show:

- quoted visible size claim
- claimant surface
- last witness time
- whether the dispute concerns `size mismatch`, `cleanup result`, `space warning`, or `capacity planning`

### 2) Counted-scope block

Must preserve:

- which subjects are counted
- whether ignored subjects are excluded
- whether placeholders contribute only namespace and metadata weight
- whether hidden Archive is excluded
- whether service-storage residue is excluded

### 3) Occupancy split block

Must split at minimum:

- namespace-only subjects
- placeholder-weight subjects
- fully materialized working subjects
- Archive occupancy
- service-storage occupancy
- temp-transfer residue
- unknown/unwitnessed occupancy

For each line show:

- byte class
- growth direction (`stable`, `can-grow`, `can-shrink`, `unknown`)
- operator actionability
- why it is or is not part of the visible size claim

### 4) Residency and cleanup block

Must review:

- whether `Remove from this device` or equivalent changed only materialization
- whether placeholders remained
- whether Archive retained older or deleted versions
- whether service-storage logs / profiler / metadata remained untouched
- whether the share is still remotely fetchable despite local byte reclamation

### 5) Blocked stronger sentence

Examples:

- `The share now occupies no meaningful space.`
- `All reclaimed bytes are permanent and globally safe.`
- `The visible size mismatch is a bug.`
- `The free-space warning was caused by the visible working tree only.`

## Hard rules

- every review must preserve the exact counted scope of the product's visible size claim
- every reclamation action must say whether it removed namespace, working bytes, Archive bytes, service-storage bytes, or only one of them
- hidden growth classes must stay visible whenever retention or background capture can enlarge them later
