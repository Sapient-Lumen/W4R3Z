# ENR drift detection & alerting (small changes, big legitimacy failures)

**Track:** A (Deployable core)


> **Threat:** attackers compromise the ENR website, its API, CDN, cache layer, localization layer, or upstream data feed to create *subtle, plausible* discrepancies that erode trust or steer narratives.

This doc defines **drift classes**, **detectors**, and a standard **DriftAlert** evidence object.

## Drift classes (what to detect)

### A) Presentation drift (UI vs API)
- Same jurisdiction/contest shows different totals between:
  - web UI vs JSON API
  - mobile vs desktop
  - different locales/languages
  - different CDNs/regions

### B) Canonical drift (CRO mismatch)
- UI/API is not derived from the signed canonical results object (CRO).

### C) Monotonicity drift
- Counts *decrease* without an explicit, signed correction reason.
- Precinct/reporting unit “percent reporting” decreases.

### D) Mapping drift
- Reporting unit boundaries/IDs change (precinct split/merge) without a precommitted mapping update anchored in PBB.

### E) Policy drift (DisclosurePolicy violations)
- Reporting granularity violates the precommitted DisclosurePolicy.
- Publishing low-cell results enabling pattern attacks.

### F) Time/order drift
- Updates appear out-of-order relative to checkpointed PBB anchors.
- ENR shows a newer timestamp but anchors to an older checkpoint.

## Adjunct checks (separate evidence objects)

Some high-value inconsistency checks are **not** “drift over time” and therefore are not encoded as `DriftAlert.class`.

### Cross-register inconsistency (VRDB ↔ results)

- Published totals must not violate basic constraints implied by VRDB aggregates (e.g., ballots accepted exceed eligible voter count for the same scope).
- Use `docs/209` and the portable `CrossRegisterConsistencyReport` evidence object for this check.

## Detector requirements
Each monitor MUST implement:
1. **CRO pinning:** fetch CRO from RRP downloads; verify signatures; verify PBB inclusion proof; verify witness checkpoint.
   - CRO hash recomputation MUST follow `235` (TBS(CRO) = omit `cro_hash` before hashing); the reference example tool is `tools/enr_drift_detector.py`.
2. **Derivation verification:** re-render EVO from CRO and compare hashes with published EVO.
3. **Cross-channel polling:** fetch from multiple regions + multiple endpoints; compare canonical hashes.
4. **Constraint checks:** monotonicity, allowed corrections, disclosure compliance.
   - include cross-register checks when eligible VRDB aggregates are available (`209`).

### Correction handling (link-forward, fail loud)

A decrease in published counts is allowed **only** when the publisher makes the correction **auditable**:

- the update is link-forward (hash chain + optional CRO linkage; see `235`), and
- the publisher declares a correction:
  - `ENRUpdate.is_correction=true` with a bounded `correction_reason` (see the compact categories in `234`), and/or
  - a `PublicNotice` with `notice_type=correction` that references both the superseded and superseding digests (`220–222`).

Corrections MUST be signed and anchored into the PBB like any other update.

## DriftAlert evidence object
When drift is detected, publish a `DriftAlert`:
- unique `alert_id`
- `election_id`
- affected scope: contest(s), reporting unit(s), endpoint(s)
- **evidence bundle**:
  - fetched artifacts (UI HTML snapshot hash, API response hash)
  - the expected CRO hash + inclusion proof
  - witness checkpoint IDs
- suggested action severity:
  - `INFO`, `WARN`, `CRITICAL`

Monitors MUST anchor DriftAlerts into the PBB so the public can verify the alert was not fabricated after-the-fact.

## Minimal public-facing rules
- ENR front-end must display the **current CRO hash** and **checkpoint ID**.
- The API must expose these same fields.
- If drift is detected by any quorum of independent monitors (policy-defined), ENR MUST show a banner linking to the DriftAlert.

## Practical monitor deployment
- Run monitors from multiple ASNs/regions.
- Use multiple resolver stacks.
- Store signed snapshots for later legal review.

## Suggested metrics
- `rrp_publish_latency`: export → anchored checkpoint
- `checkpoint_gap`: time since last witness quorum checkpoint
- `drift_rate`: drift events per hour, by class
- `correction_rate`: corrections per hour (spikes are suspicious)
