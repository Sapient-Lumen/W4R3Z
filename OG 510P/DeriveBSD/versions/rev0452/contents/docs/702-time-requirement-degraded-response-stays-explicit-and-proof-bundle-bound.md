# Time requirement degraded response stays explicit and proof-bundle-bound

**Tier:** A (Core)  
**Profiles:** A, B, C, D  
**Pillars:** supply-chain, operability  
**Patterns:** Plan→Apply→Receipt, Registry→Diff→Gate

`docs/468-trustworthy-time-posture-by-profile.md` already fixed the large product-shape posture for trustworthy time.
This page closes the next smaller loophole that would otherwise undo it:

> when time is degraded, the workflow response cannot live in daemon defaults, local shell habit, or one-off trusted-UI wording.

DeriveBSD now keeps that answer on the reviewed requirement object itself.

See also:
- ADR: `adrs/ADR-0292-time-requirement-degraded-time-response-stays-explicit-and-proof-bundle-bound.md`
- profile defaults: `docs/468-trustworthy-time-posture-by-profile.md`
- time evidence spine: `docs/227-time-discipline-and-trustworthy-timestamps-as-evidence.md`
- time monitors: `docs/308-time-monitors-and-lie-detection.md`
- schemas: `spec/time.requirement.schema.json`, `spec/time.sync.snapshot.schema.json`, `spec/time.proof.bundle.schema.json`

## Accepted boundary

### 1) `time-requirement` must say what happens when time is bad

Every reviewed `time-requirement` now carries `degraded_response`.
That object is the authoritative answer to:

- what happens if time is `degraded`
- what happens if time is `unsynced`

This keeps expiry-sensitive workflow behavior out of backend-private conditionals.

### 2) The allowed response vocabulary stays small

`degraded_response.on_degraded` may be:

- `deny`
- `repair-only`
- `allow-if-proof-fresh`
- `allow-breakglass-only`

`degraded_response.on_unsynced` may be:

- `deny`
- `repair-only`
- `allow-breakglass-only`

This is intentionally narrow.
If a workflow wants anything richer, that belongs in a new ADR or a stronger explicit lane, not in a convenient enum explosion.

### 3) `allow-if-proof-fresh` means exact proof, not “the daemon looked okay”

A workflow may proceed under degraded time only if policy explicitly says `allow-if-proof-fresh`.
When that happens, the evaluated `time.sync.snapshot` must carry `inputs.proof_bundle_digest` for the exact `time-proof-bundle` that justified the action.

That proof bundle must be:

- tied to the active `time-source-policy`
- `agreement.in_quorum = true`
- recent enough for `time-requirement.bounds.max_age_seconds`

This is the first crisp answer to “how do we keep degraded time from becoming folklore authority?”
We keep the join typed.

### 4) Unsynced time never silently proceeds

The archive now rejects the most dangerous convenience path:

- no normal “continue under unsynced time because the operator feels lucky” posture
- no backend-specific hidden weak-time fallback
- no support claim that a workflow was time-gated without an explicit gate object saying so

If `state = unsynced`, the reviewed choices are only:

- deny
- repair-only
- breakglass

### 5) Proof bundles remain stronger side evidence, not routine support truth

This cut does **not** turn `time-proof-bundle` into the ordinary support-handoff surface.
Routine support/export still stays on compact digest-first bundle joins like:

- `time_source_inventory_digest`
- `time_sync_snapshot_digest`
- `time_sync_receipt_digests`

The proof bundle only becomes mandatory when a workflow explicitly relies on `allow-if-proof-fresh`.
That keeps A/B/C/D operable without making transcript-bearing evidence ambient.

## Cross-profile fit

- **A / fleet host:** expiry-sensitive verification can require proof-backed degraded operation without allowing interactive waiver folklore; secret release and stronger authority issuance can stay stricter.
- **B / workstation:** trusted UI can explain a real reviewed response (`repair-only`, `breakglass`, or proof-backed continue) instead of inventing per-screen wording.
- **C / general-purpose OS:** explicit compatibility/admin fallback remains possible, but it must still compile to a typed requirement rather than a hidden weak-time default.
- **D / appliance / regulatory:** offline/signed-time/bootstrap lanes can be strict without pretending every degraded-time case is identical to ordinary networked sync.

## Small hard decisions made here

This page decides:

- degraded-time response is a reviewed requirement field
- proof-backed degraded continuation must bind to an exact `time-proof-bundle`
- unsynced time cannot silently continue
- `time.sync.snapshot` is where the proof join becomes inspectable

It does **not** decide:

- exact monitor/escalation loops for long-running source disagreement
- final signed offline-time token shape
- workstation repair UX details
- exact purpose-by-purpose defaults for every future requirement catalog

That is the right cut for getting from time posture prose to buildable policy/evidence behavior.

## Related docs

- `adrs/ADR-0292-time-requirement-degraded-time-response-stays-explicit-and-proof-bundle-bound.md`
- `docs/468-trustworthy-time-posture-by-profile.md`
- `docs/227-time-discipline-and-trustworthy-timestamps-as-evidence.md`
- `docs/200-secure-time-bootstrapping.md`
- `docs/283-trustworthy-time-nts-roughtime-and-lkgt.md`
- `docs/307-time-sources-in-practice-chrony-nts-and-roughtime.md`
- `docs/308-time-monitors-and-lie-detection.md`
- `spec/time.requirement.schema.json`
- `spec/time.sync.snapshot.schema.json`
- `spec/time.proof.bundle.schema.json`

Last updated: 2026-03-23r433
