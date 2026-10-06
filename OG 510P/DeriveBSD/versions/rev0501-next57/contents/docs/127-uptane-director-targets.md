# Uptane lessons (TUF + *director* role) for fleet-safe updates

TUF secures *repositories*; Uptane extends the model for **fleet / safety-critical** systems by explicitly separating:
- *Image repository* (where bytes live)
- *Director* (which decides what a specific device should install)

Uptane is a secure software update framework that starts from TUF’s design and threat model, then adds mechanisms for ECU/fleet realities. (references: https://uptane.org/docs/2.1.0/standard/uptane-standard , https://uptane.org/learn-more/design)

## Why this matters for DeriveBSD

DeriveBSD already wants:
- signed artifacts + provenance
- policy-governed deployment plans
- rollback/health-gating

Uptane’s extra lesson is: **“what should this node install?” is a separate signed decision** from “are these bytes authentic?”

That maps cleanly to DeriveBSD’s `Plan` + policy decision records:
- The `Artifact` can be valid and signed, yet *not authorized for this host* (staged rollout, model gating, region gating, incident stop).

## A minimal “Uptane-ish” lane (v1)

- Keep TUF-style repository metadata for bytes (targets).
- Add a *director-signed* “assignment” object:
  - host identity / cohort / hardware model
  - allowed generation id(s) or constraints
  - rollout window + urgency
  - required health gates (and failure handling)

- Require **threshold signing** for director keys (policy: N-of-M), to reduce blast radius of a single compromised signer.

## What we do NOT import (yet)

- Full automotive ECU graph machinery.
- Multi-ECU dependency handling.

Related: `docs/61-channel-metadata-tuf-inspired.md`, `docs/62-replay-rollback-freeze.md`, `docs/93-policy-decision-records.md`, `docs/112-health-gated-updates.md`.

Last updated: 2026-02-23
