# ADR-0227: Incident bundles carry secret-state and action proof by digest

Date: 2026-03-21
Status: Accepted

## Context

DeriveBSD already treats secrets as a typed, metadata-first lane rather than a side channel.
`docs/223-secrets-and-key-management-as-evidence.md` already established the secret lane:

- `secret-policy` declares inventory and access rules,
- `secret-grant` / lease-shaped authority bound secret access,
- `secret-receipt` records provisioning / rotation / materialization actions,
- and `secret-snapshot` is the safe metadata-only view of current secret health and rotation state.

The official incident/support-bundle contract still lagged behind that decision in practice.
`incident.bundle` already had the `secret_snapshot` / `secret_receipts` selectors plus `secret_snapshot_digest` / `secret_receipt_digests` metadata fields, but the archive still did not explicitly treat that pair as official support-handoff proof when credential health, rotation, unseal, or materialization materially shaped the incident.
Canonical `bundle.plan` examples also failed to exercise the existing include knobs, which made the secret lane look optional in prose but not yet real in the support-handoff contract.

That omission is expensive because it blurs two distinct questions:

- what safe secret state existed at capture time,
- and which exact secret actions materially participated in the incident.

Without an explicit join, support gets ticket prose, provider dashboards, or ad hoc screenshots instead of a typed answer about credential posture and exact secret actions.

## Decision

**Incident/support bundles may carry secret state and action proof by typed digest join.**

1. **Treat the existing secret selector + metadata surfaces as official support-handoff surfaces.**
   - `secret_snapshot` / `secret_snapshot_digest` identify the exact metadata-only `secret-snapshot` that describes current secret health, rotation posture, and latest receipt linkage at capture time.
   - `secret_receipts` / `secret_receipt_digests` identify the exact `secret-receipt` objects proving provisioning / rotation / unseal / materialization actions that materially shaped the incident.

2. **Keep safe state context distinct from action proof.**
   - `secret_snapshot_digest` answers what bounded secret state existed at capture time.
   - `secret_receipt_digests` answer which exact secret actions participated.
   - This ADR does not collapse the secret lane into a generic "credential dump" or provider export.

3. **Keep the support-handoff lane metadata-only.**
   - `secret-snapshot` and `secret-receipt` remain metadata-only objects.
   - This ADR does not bless raw secret bytes, plaintext env files, provider response bodies, or ad hoc screenshots as ordinary support-bundle truth.

4. **Make the shared bundle-plan include surface real for the secret lane too.**
   - `spec/incident.bundle.schema.json#/$defs/include_knobs` already carries `secret_snapshot` and `secret_receipts`.
   - `bundle.plan.selection.include` must exercise those selectors when secret health or exact secret actions materially shaped the incident/support story.

5. **Use the secret joins when they materially shape the story.**
   - Bundles should include `secret_snapshot_digest` when responders need a typed answer about safe current credential posture.
   - Bundles should include `secret_receipt_digests` when rotation, unseal, materialization, or other secret actions materially participated in the incident.
   - Bundles do not need to carry every historical secret receipt.

## Consequences

- Official support handoff can now explain secret health and exact secret actions without teaching support to trust provider dashboards, ticket notes, or screenshots.
- Canonical bundle examples become mechanically checkable instead of placeholder-shaped for the secret lane.
- The archive keeps a narrow boundary: no new subsystem, no secret-value export path, and no promotion of provider-private debug output into routine support truth.

## Alternatives considered

- **Leave secret joins implicit in prose.** Rejected: the schema already has the right surfaces, but implementers still need the archive to say they are official support-handoff truth.
- **Carry only `secret_receipt_digests`.** Rejected: exact action proof is not the same as a safe answer about current secret health / rotation posture at capture time.
- **Add a generic `credential_dump` or provider-debug field.** Rejected for now: it widens the routine handoff contract and fights the metadata-first secret lane.
- **Let provider dashboards or screenshots explain secret state.** Rejected: that recreates implementation-private folklore and weakens explainability across A–D.

## Status

Accepted and wired through the canonical bundle examples, the secret/support-bundle docs, and archive hygiene checks.
