# 181 — Publication contract + deadline breach proofs

**Track:** A (Deployable core)

## Purpose
This archive treats **delayed publication** as an outcome/legitimacy attack.

We therefore make evidence publication time-bounded and **auditable**:

1) publish a signed `PublicationContract` early (before election day),
2) treat deadlines as verifiable promises (MMD-style),
3) when a deadline is missed, produce a signed `PublicationSuppressionReport` that is
   itself receipted + gossiped, making “they never published it” **portable**.

This extends `docs/145` (MMD-style deadlines) and `docs/180` (receipts + gossip) into a
single contract that observers can point to.

## Contract object
Envelope kind: `hfv.publication.contract`  
Payload schema: `schemas/PublicationContract.json`

A contract is a list of rules keyed by `EvidenceEnvelope.kind`, each defining:

- a named `trigger` event,
- a deadline class (`MMD-PBB`, `MMD-EVID`, `MAAD`, or `CUSTOM`),
- `max_delay_seconds` after the trigger,
- whether attachment requirements come from the registry (recommended) or are explicit.

### Minimal recommended rules (Track A)
- `hfv.results.enr_update` → `MMD-EVID`
- `hfv.coverage.report` → `MMD-EVID`
- `hfv.inspection.challenge_schedule` → `MMD-EVID`
- `hfv.inspection.suppression_report` → `MMD-EVID`
- `hfv.publication.suppression_report` → `MMD-EVID` (self-hardening)

## Deadline breach proof
Envelope kind: `hfv.publication.suppression_report`  
Payload schema: `schemas/PublicationSuppressionReport.json`

A suppression report is issued when an observer believes an expected evidence kind
did not appear before the deadline stated in the contract.

Important: negative proofs are hard. The goal is not a perfect cryptographic
non-existence proof; the goal is to make **selective delay/suppression contestable**
with signed statements + probe records + multi-perspective corroboration, and to
force the verification ecosystem to confront and disseminate “missingness”.

## Interop note
This document intentionally does **not** lock the receipt wire format.
Receipts/gossip attachments remain generic objects (see `docs/180`), with optional
profile mapping guidance in `docs/182`.

## Links
- `docs/145-mmd-style-deadlines-for-evidence-publication.md`
- `docs/180-receipts-and-gossip-attachments.md`
- `docs/176-canonicalization-and-signing-rules-for-evidence-envelopes.md`


## Trigger events (portable anchors)

`hfv.publication.trigger_event` (docs/187) is a portable, receipted+gossiped declaration that a deadline trigger occurred. Suppression reports SHOULD reference the trigger event envelope/object in `trigger.reference` so independent verifiers can recompute deadlines.

## Second-order missingness (defense in depth)

An attacker may try to suppress **suppression reports** themselves. The design response is not “perfect negative proofs,” but **multiple independent publication surfaces**:

- Suppression reports MUST be receipted + gossiped (registry) and SHOULD be mirrored broadly.
- Watchers SHOULD *echo* observed suppression reports (re-publish the digest in a PublicNotice or feed) to move the missingness signal across failure domains.
- Independent watchers SHOULD publish receipted+gossiped **LivenessBeacons** (`hfv.coverage.liveness_beacon`, docs/210) that record reachability and observed digests for the public pointer surfaces (well-known/directory/feed/keyset). This makes “missingness about missingness” harder to bury.
- Where available, attach independent corroboration objects (e.g., OONI corroboration, multi-vantage parity snapshots) so the dispute is not purely “my word vs theirs.” See `docs/119` and `docs/201`.
