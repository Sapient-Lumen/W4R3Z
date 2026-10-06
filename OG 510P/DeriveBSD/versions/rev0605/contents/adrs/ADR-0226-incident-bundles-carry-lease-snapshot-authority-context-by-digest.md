# ADR-0226: Incident bundles carry lease-snapshot authority context by digest

Date: 2026-03-21
Status: Accepted

## Context

DeriveBSD already treats temporary authority as typed, bounded, and queryable rather than ambient.
`docs/249-lease-registry-and-cross-lane-revocation.md`, `docs/252-lease-envelope-and-cross-lane-joins.md`, and `docs/449-lease-issue-and-use-receipts.md` already established the lease lane:

- lane-specific grant / lease / session objects remain authoritative,
- `lease.issue.receipt` and `lease.use.receipt` remain evidence-only,
- `lease-revoke-event` records revocation attempts and results,
- and `lease-snapshot` is the safe metadata view of what temporary authority was live at capture time.

The official incident/support-bundle contract still lagged behind that decision in practice.
`incident.bundle` already had the `lease_snapshot` selector and `lease_snapshot_digest` field, and canonical bundle plans already exercised `lease_snapshot`, but the archive still did not explicitly treat the exact `lease.snapshot` as official support-handoff context when live temporary authority materially shaped the incident.
That left too much room for authority context to drift back toward bastion dashboards, control-plane screenshots, operator memory, or chat archaeology.

That omission is expensive because it blurs two distinct questions:

- which exact bounded sessions / grants / receipts participated in the incident,
- and what temporary authority was still live at handoff time even if it had not yet been exercised.

Without an explicit join, support receives proof of individual support/operator/breakglass/secret actions but still has to reconstruct the surrounding “what authority was live?” state from side systems.

## Decision

**Incident/support bundles may carry temporary-authority context by typed digest join.**

1. **Treat the existing lease selector and metadata field as an official support-handoff surface.**
   - `lease_snapshot` / `lease_snapshot_digest` identify the exact bounded `lease.snapshot` that describes what temporary authority was live at capture time.
   - This join is for authority context, not for replacing lane-specific authoritative grant / lease / session objects.

2. **Keep live-authority context distinct from participation proof.**
   - `support_session_digests`, `operator_session_digests`, `breakglass_receipt_digests`, `secret_receipt_digests`, and similar fields prove which exact bounded actions or sessions participated.
   - `lease_snapshot_digest` answers the different question of what temporary authority was still live when the bundle was captured.
   - This ADR does not collapse all temporary-authority evidence into a generic “authority dump” field.

3. **Make the shared bundle-plan include surface real for lease context as well.**
   - `spec/incident.bundle.schema.json#/$defs/include_knobs` already carries `lease_snapshot`.
   - `bundle.plan.selection.include` must exercise that selector when support handoff needs bounded temporary-authority context instead of retelling the story from bastion dashboards or ticket notes.

4. **Use the snapshot join when live authority materially shaped the story.**
   - Bundles should include `lease_snapshot_digest` when support, operator, breakglass, secret, publish-session, or other temporary-authority state materially shaped the incident/support story.
   - Bundles do not need to carry every historical snapshot.

5. **Do not promote side systems into bundle truth.**
   - This ADR does not bless bastion dashboards, control-plane screenshots, or chat notes as the canonical support-handoff source of live authority state.
   - Those remain auxiliary or stronger side-evidence lanes under explicit export policy.

## Consequences

- Official support handoff can now answer both “what exact bounded actions participated?” and “what temporary authority was still live at capture time?” without leaving the typed bundle contract.
- Canonical examples become mechanically checkable instead of placeholder-shaped for the lease snapshot lane too.
- The archive keeps a narrow boundary: no new subsystem, no generic authority-debug blob, and no promotion of side dashboards into routine support truth.

## Alternatives considered

- **Rely on support/operator/breakglass/session digests alone.** Rejected: participation proof is not the same as the bounded live-authority context at capture time.
- **Add a generic `authority_context_digests` or `authority_dump` field.** Rejected for now: the archive already has the typed `lease.snapshot` surface for normal support handoff, and a broader field would widen the routine contract before it is needed.
- **Let bastion dashboards, chat logs, or operator memory tell the story.** Rejected: that recreates implementation-private folklore and weakens portability / explainability across product shapes.

## Status

Accepted and wired through the bundle examples, lease/support-bundle docs, curated lease references, and archive hygiene checks.
