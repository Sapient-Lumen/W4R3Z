# Trustworthy time as an input (Roughtime + last-known-good time)

DeriveBSD relies on time in a few places:

- update metadata expiry (TUF-style channels)
- transparency evidence freshness (logs/receipts)
- policy rules like “do not accept artifacts older than X”

If an attacker can set the clock backwards (or freeze it), **signed** metadata can still be abused.
So time should be treated as a **policy-governed input** with evidence, not an ambient assumption.

## Lesson to steal

- require at least one *verifiable* time source for high-assurance channels (Roughtime and/or NTS)
- maintain a local **last-known-good time (LKGT)** and never accept time earlier than LKGT
- store LKGT in a tamper-resistant place when available (TPM NV, sealed file, state dataset)

## DeriveBSD mapping (optional, policy-gated)

### Evidence object: time proof bundle

When a workflow needs trustworthy wall-clock time (verification, promotion, activation), capture a proof bundle:

- `time-proof-bundle` (`spec/time.proof.bundle.schema.json`)
  - per-source observations (Roughtime/NTS)
  - uncertainty bounds and quorum agreement
  - digest references to protocol transcripts

This keeps “why did we accept this expiry window?” explainable.

### Operational integration: time sync snapshots + receipts

Use the operational time lane for continuous discipline and history:

- `time-sync-snapshot` (`spec/time.sync.snapshot.schema.json`)
  - current sync state + uncertainty
  - optional LKGT fields (monotonic floor)

- `time-sync-receipt` (`spec/time.sync.receipt.schema.json`)
  - steps/slews/source changes
  - optional LKGT before/after

See: `docs/227-time-discipline-and-trustworthy-timestamps-as-evidence.md`.

### Verification rule sketch

1) gather verifiable time observations under `time-source-policy`
2) compute a conservative “now” interval `[t_min, t_max]`
3) enforce `t_min >= LKGT` (if LKGT is enabled)
4) apply expiry/freshness checks using conservative bounds
5) advance LKGT monotonically after success

### Air-gapped nuance

If no online source exists, policy can:

- allow operator-provided signed time tokens (offline authority)
- accept RTC-only but mark operations as `degraded_time` (evidence required)

Last updated: 2026-02-25
