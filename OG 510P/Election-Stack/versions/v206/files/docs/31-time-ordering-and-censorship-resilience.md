# Time, ordering fairness, and censorship resilience

**Track:** A (Deployable core)

## Why this exists
Attackers can win without breaking crypto by:
- manipulating time sources (clock skew / NTP attacks),
- partitioning networks (regional blackouts),
- selectively dropping ballots (targeted suppression),
- exploiting ordering rules (especially if revoting exists).

This document defines hardened time and ordering rules.

See also: `docs/38-secure-time-and-ordering.md` and `docs/192-time-attestation-and-timestamping-as-evidence.md`.

## 1) Time sources (normative)

1. Clients MUST NOT rely on a single time source.
2. Federation nodes and witnesses SHOULD publish signed **time beacons** (e.g., `hfv.time.beacon` envelopes).
3. Receipt state transitions MUST be based on **log checkpoints**, not wall-clock time alone.

Operational recommendation:
- Prefer authenticated time sync (e.g., NTS for NTP) (`source: rfc8915_txt`) over unauthenticated NTP (`source: rfc5905_txt`).
- Use rough-time protocols that support misbehavior proofs when bootstrapping or in hostile networks (`source: draft_ietf_ntp_roughtime_17_txt`).

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
