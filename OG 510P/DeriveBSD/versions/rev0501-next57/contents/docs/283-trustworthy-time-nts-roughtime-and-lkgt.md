# Trustworthy time: NTS + Roughtime + LKGT (make time a verifiable input)

Time is a hidden dependency for:
- update metadata expiry
- transparency receipt freshness
- anti-rollback rules (“don’t accept artifacts older than X”)

If an attacker can set the clock backwards (or freeze it), *signed* metadata can still be abused.
So time should be treated as a **policy-governed input** with evidence.

This doc is a bridge between:
- “secure time sources” (`docs/227-time-discipline-and-trustworthy-timestamps-as-evidence.md`)
- “rough trustworthy time for expiry safety” (`docs/142-trustworthy-time-roughtime.md`)

## DeriveBSD time objects (already in the archive)

- Source inventory: `spec/time.source.inventory.schema.json`
- Source allowlist + quorum: `spec/time.source.policy.schema.json`
- Proof bundle (captures NTS/Roughtime observations): `spec/time.proof.bundle.schema.json`
- Time sync plan/snapshot/receipt: `spec/time.sync.plan.schema.json`, `spec/time.sync.snapshot.schema.json`, `spec/time.sync.receipt.schema.json`

## LKGT (last-known-good time) as an explicit invariant

“Last-known-good time” (LKGT) is a simple anti-rollback primitive:
- never accept a time earlier than LKGT
- advance LKGT monotonically when a workflow succeeds

DeriveBSD should treat LKGT as part of operational time discipline:
- included in time snapshots (so health gates can reference it)
- emitted in time-sync receipts on any step/bootstrap

This makes “why did we accept this expiry window?” explainable.

## Policy sketch

A high-assurance channel can require:
- `time-source-policy.quorum.min_sources >= 2` for stricter A/D steady-state floors
- authenticated sources (NTS or Roughtime)
- max skew bound
- LKGT monotonicity

A bootstrapping policy can allow degraded time:
- RTC-only (bounded age)
- operator-provided offline time tokens (treated as a source class)

Ordinary degraded-time continuation is no longer implicit: a reviewed `time-requirement` must now say whether the workflow denies, repairs, breakglasses, or may `allow-if-proof-fresh` with an exact `time-proof-bundle` join.

Concrete profile floors now live in `docs/722-time-source-policy-profile-floors-stay-finite-and-profile-mapped.md`. That doc fixes the finite A/B/C/D source-count, protocol-mix, quorum, skew, and RTC-bootstrap floors so the policy sketch here no longer has to stand in for product truth.

## Where this plugs in

- TUF-style channel verification: `docs/61-channel-metadata-tuf-inspired.md`
- Freeze/rollback rules: `docs/62-replay-rollback-freeze.md`
- Rollout gates: `docs/112-health-gated-updates.md`, `docs/258-staged-rollouts-and-cohorts.md`
- Transparency freshness: `docs/257-release-capsules-and-transparency.md`, `docs/259-transparency-monitors-and-witness-gossip.md`

See also: `docs/308-time-monitors-and-lie-detection.md` (fleet-level lie detection + alerts).

Last updated: 2026-03-23r453
