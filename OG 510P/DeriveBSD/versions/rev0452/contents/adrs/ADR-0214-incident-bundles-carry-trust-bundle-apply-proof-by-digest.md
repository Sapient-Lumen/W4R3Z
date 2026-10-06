# ADR-0214: Incident bundles carry trust-bundle apply proof by digest

- Status: Accepted
- Date: 2026-03-21

## Context

`ADR-0212` and `docs/622-trust-bundle-apply-receipts-bind-canonical-bundles-to-runtime-views.md` already fixed the **runtime truth** boundary for trust roots:

- canonical `pki-trust-bundle` objects stay authoritative,
- `pki.trust.bundle.diff` stays the review surface,
- and `pki.trust.bundle.apply.receipt` proves **what exact trust view a host or unit actually served**.

That still left one practical support/export gap:
**the official incident/support bundle contract could include the canonical trust bundle digest, but it still had no typed place for the apply-proof receipts that explain what was really active.**

That omission is expensive because it quietly re-opens the same folklore boundary `ADR-0212` closed:

- support bundles can say which trust bundle was intended without proving which runtime trust view was actually served,
- responders fall back to renderer-specific store dumps, control-plane status pages, or shell archaeology,
- trust-view activation changes become visible in `pki-event` but disappear from the official bundle handoff,
- and the canonical bundle + runtime-view proof split stops composing with the official bundle contract right where incident/debug/export flows need it.

The archive already has the right pattern for this.
We do **not** need a new PKI bundle subsystem.
We need the official incident-bundle selector and metadata surfaces to carry the typed apply proof by digest.

## Decision

**Incident/support bundles may carry trust-bundle apply proof by typed digest joins.**

Specifically:

1. Extend the canonical bundle include-knob surface.
   - `spec/incident.bundle.schema.json#/$defs/include_knobs` must carry `pki_trust_bundle_apply_receipts`.
   - Because `bundle.plan.selection.include` reuses that shape, official bundle planning inherits the same selector automatically.

2. Extend the canonical bundle metadata surface.
   - `incident.bundle.includes` must carry `pki_trust_bundle_apply_receipt_digests`.
   - These digests point at `pki.trust.bundle.apply.receipt` objects, not at renderer-private dumps.

3. Keep review and apply proof distinct inside support handoff.
   - `pki_trust_bundle_digest` remains the digest of the canonical reviewed trust bundle.
   - `pki_trust_bundle_apply_receipt_digests` are the activation proof for what was actually served.
   - Neither field replaces `pki.trust.bundle.diff`; review and activation remain separate surfaces.

4. Keep the rule conditional and narrow.
   - Incident bundles should include recent trust-bundle apply receipts **when trust-view activation changed or is relevant to the incident/support story**.
   - This does not mean every bundle must always include every historical trust-view apply receipt.

5. Do not promote renderer/distributor state into the authority model.
   - The official join is the digest of the canonical bundle plus the digest(s) of `pki.trust.bundle.apply.receipt`.
   - Raw adapter dumps and distribution-specific views remain explicit stronger/debugging evidence, not the default bundle truth.

## Consequences

- Support bundles can now answer both **what trust roots were approved** and **what exact trust view was actually served**.
- The official support handoff stays aligned with `ADR-0212` instead of partially undoing it.
- `bundle.plan` / `incident.bundle` remain the one official bundle-selection and metadata contract for this evidence lane too.
- Future PKI/runtime incidents no longer need renderer-specific folklore just to explain the active trust view.

## What this does not decide

This ADR does **not** decide:

- the final trust-bundle apply retention window,
- whether every bundle template enables the selector by default,
- the richer export path for raw trust-store diagnostics,
- or any new trust-view renderer/distributor API.

It only fixes the missing typed join between the already-decided trust-view apply receipt and the already-decided incident/support bundle contract.
