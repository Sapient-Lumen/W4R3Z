# Time, ordering fairness, and censorship resilience

**Track:** A (Deployable core)


## Why this exists
Attackers can win without breaking crypto by:
- manipulating time sources (clock skew / NTP attacks),
- partitioning networks (regional blackouts),
- selectively dropping ballots (targeted suppression),
- exploiting ordering rules (especially if revoting exists).

This document defines hardened time and ordering rules.

## 1) Time sources (normative)

1. Clients MUST NOT rely on a single time source.
2. Federation nodes and witnesses MUST publish signed **time beacons** periodically.
3. Receipt state transitions MUST be based on **log checkpoints**, not wall-clock time alone.

## 2) Ordering rules

### 2.1 Canonical order
The only canonical order is the transparency log order committed by witness-quorum checkpoints.

### 2.2 Revoting
If revoting is enabled:
- “last vote counts” MUST be defined strictly by canonical log order.
- any revote invalidation MUST be provable from the public log.

## 3) Censorship evidence (two-phase acceptance)

### 3.1 Intake receipt
A node MAY issue an `IntakeReceipt` that promises inclusion by deadline `T`.

### 3.2 Failure to include
If inclusion proof is not available by `T`, the client MUST surface:
- NOT RECORDED
- publishable evidence that the node accepted intake but did not record.

## 4) Partition strategy
- Multiple submission entrypoints MUST exist (multi-homing).
- Clients SHOULD support opportunistic submission to multiple nodes.
- The system MUST provide an offline fallback (poll-site / paper / kiosk), and MUST communicate it clearly.
