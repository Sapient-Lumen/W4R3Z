# 38 — Secure time and ordering

**Track:** A (Deployable core)


This system has several mechanisms that depend on **time and ordering**:

- Revoting / “last vote counts” rules
- Intake deadlines (“must be included by T+Δ or publish drop evidence”)
- Poll open/close boundaries
- Rate limits and anti-replay protections
- Evidence bundle timelines (publication schedules)

## Threats

### T1 — Time shifting / time confusion
Attackers manipulate a voter’s or node’s notion of time to:
- cause premature “polls closed” errors
- cause a ballot to miss a deadline
- confuse revote ordering
- enable replay windows or defeat expiration checks

Classic NTP deployments are frequently unauthenticated; an on-path attacker can influence client clocks.

### T2 — Forked time sources
Different parts of the federation use different clocks → inconsistent behavior, litigation risk, and “he said / she said” disputes.

### T3 — “Time as an oracle”
If the system publishes fine-grained timing events, it can enable coercion or traffic analysis.

## Design principles

1. **Canonical ordering comes from the log**, not from wall-clock time.
2. **Wall-clock time is advisory** and used only for UI and coarse boundary checks.
3. **Any time assertions that affect correctness MUST be cryptographically provable**, and MUST tolerate some time sources being dishonest.

## Normative requirements

### Canonical ordering
- The **only** canonical ordering for ballots (including revote precedence) is the order of entries in the **witness-quorum checkpointed** public bulletin board (PBB).
- Nodes and verifiers MUST derive revote precedence and “counted ballot” decisions from `(Checkpoint.tree_size, entry_index)` and MUST NOT use local time to break ties.

### Checkpoint time
- Each checkpoint MUST carry a **time attestation**:
  - either (a) a quorum of witness signatures over a timestamp, or
  - (b) a signature over a timestamp plus an externally verifiable proof (e.g., secure time protocol proof), or
  - (c) both.
- Verifiers MUST treat checkpoint timestamps as **untrusted** unless they satisfy the configured TimeBeacon policy.

### Secure time protocol (recommended)
Use a secure rough time protocol such as **Roughtime**:
- Clients SHOULD query **multiple independent Roughtime servers**.
- Clients MUST retain cryptographic proofs from Roughtime queries that can demonstrate misbehavior (lying servers).
- Clients MUST apply a plausibility window (e.g., “time must be within ±W of last known good time”) and MUST surface errors loudly.

### Randomness beacons for fairness / tie-breaking (optional)
For any process that requires public randomness (audit sample selection, tie-breaking, etc.), use a **public randomness beacon** with published, verifiable outputs.

- The system MAY support NIST’s Interoperable Randomness Beacon 2.0 (or another publicly auditable beacon) for seed material.
- All randomness-dependent procedures MUST be reproducible from the published beacon outputs and the published procedure transcript.

## Implementation notes (TCB minimization)

- Treat time verification logic as security-critical; keep it small and well-tested.
- Ensure “deadline missed” logic cannot be triggered by minor clock skew; rely on **log ordering + checkpointing**.
- Publish only what is necessary: avoid releasing per-voter fine-grained times.

## Evidence artifacts

- `schemas/TimeBeacon.json` — policy-bound time attestations
- `schemas/Checkpoint.json` — includes timestamp + witness cosignatures
- `artifacts/checklists/secure-time-checklist.md`