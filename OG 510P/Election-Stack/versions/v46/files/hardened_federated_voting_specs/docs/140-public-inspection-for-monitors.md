# Public inspection for third‑party monitors

**Track:** A (Deployable core)


## Goal
Monitors are a critical control point: they decide whether equivocation, split views, or missing artifacts are discovered and escalated.

This document specifies a **public inspection** mechanism so that monitors can be *verified as performing the work they claim*, and so that a compromised or negligent monitor can be detected.

## Threats addressed
- **Paper monitors**: listed as “active” but not running.
- **Targeted blindness**: monitor ignores specific artifacts (e.g., a particular jurisdiction/locale).
- **Selective disclosure**: monitor reports different findings to different parties.
- **Implementation flaws**: monitor returns incorrect results due to bugs or misconfiguration.

## Core mechanism
### 1) Monitor Attestation (MA)
Each monitor MUST periodically publish a signed `MonitorAttestation` containing:
- monitor identity and software provenance
- coverage claims (what logs/endpoints/regions/locales it checks)
- recent checkpoint IDs and hashes observed
- summary of alerts issued (with hashes)

These attestations MUST be anchored in the evidence chain (PBB checkpoint / ATL checkpoint).

### 2) Watcher‑issued public challenges
Any watcher (party, NGO, press, auditor) MAY issue a signed `PublicInspectionChallenge`:
- includes a set of targets (artifact hashes, endpoints, locales)
- includes a time window
- requests the monitor to return evidence (inclusion proofs, parity results, consistency proofs)

The challenged monitor MUST respond with a signed `PublicInspectionResponse`.

### 3) Cross‑monitor consistency
Watchers SHOULD issue identical challenges to multiple monitors. If responses disagree, watchers MUST publish a `MonitorInconsistencyReport`.

## Minimum requirements
- At least **K** monitors from distinct operator categories MUST be continuously active.
- Each monitor MUST support offline replay of its results from published evidence bundles.
- Monitors MUST publish failure states (downtime, partial coverage) as signed events.

## Operational notes
- Challenges should be rate‑limited to avoid DoS.
- Challenge sets should include “canary” artifacts whose inclusion is known.

## Schemas
- `schemas/PublicInspectionChallenge.json`
- `schemas/PublicInspectionResponse.json`
- `schemas/MonitorInconsistencyReport.json`