# Successor capsule contract sheet page — cold import, seat rebirth, and carry-forward boundary

## Purpose

Show, in one durable place, the exact continuity contract of a reviewed successor artifact before or after export/import.

This page exists to answer:

- `what does this capsule actually carry forward?`
- `what definitely does not survive import?`
- `does the replacement seat keep the old identity or get a new one?`
- `what stronger continuity sentence is blocked?`

## Required sections

### 1. Capsule header

Must show:

- successor capsule id
- capsule family (`device-replacement`, `state-root-migration`, `seat-recovery`, `inspection-only`, `other`)
- source world id
- export time
- current validity (`fresh`, `stale-review-needed`, `expired`, `consumed`, `revoked`)

### 2. Carry-forward matrix

Must list at least these rows separately:

- subject roster
- subject-local policy
- approval / trust memory
- lineage receipts
- helper/bootstrap residue
- caches and ephemeral route observations
- in-flight execution tickets
- durable evidence/history

Each row must state one of:

- `carried forward unchanged`
- `carried forward but narrowed`
- `recomputed on import`
- `dropped by design`
- `unknown; proof insufficient`

### 3. Seat rebirth block

Must show separately:

- predecessor seat handle
- successor seat handle policy (`preserve`, `rebirth-required`, `reviewed-optional`, `not-applicable`)
- certificate / proof-handle posture
- whether linked-family membership, requester trust, or peer memory must be rereviewed

The page must answer:

> is this the same seat, a reborn successor seat, or only subject state carried to a new seat?

### 4. Predecessor boundary block

Must show:

- whether predecessor runtime must already be stopped
- whether predecessor seat must be retired, hidden, revoked, or left inspect-only
- whether concurrent activation is blocked
- what duplicate-seat sentence is explicitly refused

### 5. Strongest safe sentence

Examples:

- `This capsule can carry reviewed subject state to a reborn replacement seat; it does not prove same-seat continuity.`
- `This capsule is inspection-only and may not be activated as a live successor.`

### 6. Blocked stronger sentence

Examples:

- `Importing this capsule makes the new machine the same seat as before.`
- `This artifact preserves every cache, lease, and trust fact exactly as they stood at export time.`

## Minimum interactions

The page must expose actions to:

- export capsule
- verify capsule
- inspect carried-forward rows
- start successor import review
- invalidate or retire capsule
- open latest lineage receipt
