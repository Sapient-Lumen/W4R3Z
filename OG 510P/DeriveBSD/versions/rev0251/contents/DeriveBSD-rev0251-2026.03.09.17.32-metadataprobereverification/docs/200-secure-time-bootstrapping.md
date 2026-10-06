# Secure time bootstrapping (NTS + Roughtime) as an evidence-bearing lane

Time is a security dependency:
- transparency log verification
- cert validity windows
- anti-rollback decisions
- build reproducibility / replay capsules

DeriveBSD already treats **time as authority** (`197-time-and-rng-authority.md`).
This doc adds a *secure-source* lane: time can be *authenticated* and *auditable*.

## Lessons to steal

- **Network Time Security (NTS)** adds cryptographic security to NTP client/server mode (NTS-KE + NTS extensions). See RFC 8915.
- **Roughtime** is an authenticated rough-time protocol designed so clients can obtain *cryptographic proof of server malfeasance*; it is intentionally quorum-friendly.

## Proposed primitive

A host service, `system.time`, that:
1) obtains time from one or more **secure sources** (NTS servers, Roughtime servers, optionally local RTC as a bounded bootstrap)
2) evaluates a **source policy** (quorum, maximum skew, trust roots)
3) issues `time-authority-grant` tokens (already defined) and produces `time-snapshot` receipts that can carry a *proof bundle digest*

This makes “what time did we believe?” **replayable** and **auditable**.

### New evidence objects

- `time-source-policy` (signed)
  - which sources are acceptable (protocol + endpoint identity)
  - how to decide “good enough” (quorum rules, skew bounds, bootstrap windows)

- `time-proof-bundle` (signed by `system.time`)
  - the raw-ish observations and the computed agreement result
  - sufficient to explain why the policy engine accepted or rejected time

The `time-snapshot` can reference a `time-proof-bundle` by digest.

## Bootstrapping model

1) **Early boot**: accept RTC (or monotonic-only) within a tight window, *only* for bringing up networking and fetching secure time.
2) **Secure convergence**:
   - query multiple NTS servers (preferred for steady-state)
   - optionally query multiple Roughtime servers (fast “rough sanity” + misbehavior proof)
3) **Lock-in**: once the `time-source-policy` quorum is met, emit an accepted `time-proof-bundle` and begin issuing high-assurance snapshots.

## Consistency and attack notes

- **MITM on NTP**: NTS is designed to provide authenticated time sync; the time proof bundle records the server identity and negotiated parameters.
- **Single time oracle** is fragile: policy should default to **N-of-M**.
- **Split view**: if different clients see different times, we want *detectable divergence*.
  - The time policy can require at least one *independent* source operator class (e.g., “2 vendors”).
  - The proof bundle captures the divergence and the chosen resolution rule.
- **Backdating attacks**: the policy engine should treat time as an input with *max drift* and require evidence for “large jumps”.

## Integration points

- `197-time-and-rng-authority.md`: profiles can carry a `time-source-policy` digest.
- `187-witnessed-transparency-checkpoints.md`: time snapshots used for checkpoint acceptance should reference a proof bundle.
- `194-debugging-by-lease-and-replay-capsules.md`: replay capsules can include “time snapshot + proof bundle digest” for forensic reproducibility.

## Open questions

- Should `system.time` expose a “proof-of-misbehavior” export format for Roughtime disputes?
- Do we want a minimal “secure time kit” that works without full PKI (for air-gapped / enclave-ish deployments)?


Implementation notes (NTS backends + Roughtime quorum wiring): `docs/307-time-sources-in-practice-chrony-nts-and-roughtime.md`.

Last updated: 2026-02-26
