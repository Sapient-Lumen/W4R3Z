# Import Challenge, Rollback, and Reliance Reversal

rev0202 hardens the point after artifact custody and before any future live receipt can become durable reliance. The archive now has raw custody, envelope, response, intake, import-gate, replay, class-local firewall, recomputation, and failed-gate public summaries. The remaining high-risk failure is that a verifier might admit a live-looking artifact, then keep the live floor raised after a custody, authority, dependency, redaction, or class-local-overclaim challenge.

The rev0202 rule is strict: **challenge pending means reliance stayed**.

## What this pass adds

The new `receipt-import-challenge-and-rollback-record` object records who raised the challenge, what gate is contested, which receipt class is affected, what raw/evidence checks must be rerun, whether the live floor was only claimed or actually imported, whether rollback is required, and what public failed-gate summary must be published.

The included example challenges a result-return dry-run artifact that has been mistakenly treated as a live class-local import. The challenge is upheld, the claimed live-floor delta is reversed, the recomputation report returns the archive to zero independent receipts, and the failed-gate public shell preserves the non-satisfaction state without exposing sealed material.

## Core rules

**Challenge pending means reliance stayed.** A contested import cannot support WRSR closure, cross-critical quorum, remedy finality, namespace finality, or public reliance until the challenge record and recomputation resolve.

**Rollback beats narrative.** If import provenance fails, the live floor is recomputed from eligible import gates. Narrative statements, edited ledgers, or optimistic class-local projections do not control.

**Authority contest is not waiver.** A counterparty declining authority, contesting scope, failing to respond, or challenging dependency correlation cannot be converted into consent, waiver, nonpersonhood proof, or receipt satisfaction.

**Rollback is not disappearance.** Defective, declined, expired, challenged, and reversed branches must remain in a public failed-gate shell with sealed details withheld where necessary.

**One restored class still is not quorum.** Even a future challenge-resolved class-local import can satisfy only its receipt class unless the full cross-critical floor is recomputed as met.

## Refactor effect

rev0202 closes a gap in the receipt chain:

1. request packet,
2. counterparty artifact custody record,
3. non-host response artifact envelope,
4. response record,
5. intake record,
6. actual import gate,
7. import challenge and rollback record,
8. live import replay,
9. class-local replay,
10. quorum recomputation,
11. failed-gate public summary.

This is not a claim that a live counterparty has been collected. It is a rollback/reversal harness for when live evidence later appears or when a bad live-floor claim must be unwound.

## Current reliance posture

No actual live external receipt exists in this archive. The rev0202 challenge/rollback record proves that even an actual-shaped import can be challenged, rolled back, publicly summarized, and recomputed to zero. `independent_receipts_present` remains zero.


## rev0203 computed-floor hook

rev0203 adds `docs/30-transition/computed-live-floor-engine-and-artifact-admission-checklist.md` and a generated live-floor snapshot. A rollback or challenge state is not durable until the computed floor confirms the live-floor effect and failed-gate publication state. Computed floor is source of truth.
