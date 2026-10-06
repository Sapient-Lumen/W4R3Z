# ADR-0185: Publish-session diagnostic artifacts stay off baseline envelope

- Status: Accepted
- Date: 2026-03-20

## Context

ADR-0152 created `net.publish.session` as the compact typed envelope for relay-backed temporary
sharing. Later cuts made that envelope more exact about audience, authority, locator posture,
secret-handoff lifetime, endpoint tuples, and lease-frozen outward surface semantics.

One smaller ambiguity still remained inside the evidence object itself:

**should the same compact publish-session envelope also point directly at backstage relay/admin
diagnostic artifacts?**

Without one more narrow decision, the archive leaves one receipt trying to be two different
surfaces at once:

- the bounded share envelope that support/UI/export may reasonably want to ship, and
- a backstage diagnostic/log surface that is often more privileged and investigation-specific.

DeriveBSD already has richer places for that second class of evidence: `support.session`,
`operator.session`, and `incident.bundle`.
It does not need `net.publish.session` itself to become a mixed baseline-plus-privileged log
container.

## Decision

1. `net.publish.session.evidence` no longer carries `diagnostic_artifact_digests`.
2. The compact publish-session evidence surface stays limited to the share-shaped summary data it
   already needs, such as:
   - `visible_indicator_posture = durable-until-ended`
   - `network_receipt_digests`

3. Richer relay/admin/debug/investigation artifacts must travel through the existing stronger
   evidence lanes (`support.session`, `operator.session`, `incident.bundle`) rather than riding on
   the compact publish-session envelope.

## Consequences

- `net.publish.session` stays closer to an export-safe share receipt instead of drifting toward a
  privileged backstage log index.
- Incident/support workflows still have a place for richer diagnostics, but that place is now one
  of the existing stronger evidence lanes rather than the baseline share envelope itself.
- Future log-taxonomy work remains open; this ADR only prevents baseline/privileged evidence blur in
  the current temporary-sharing lane.

## Alternatives considered

- **Keep `diagnostic_artifact_digests` on `net.publish.session`.** Rejected because it blurs the
  share envelope with backstage diagnostics and makes export/support surfaces guess whether the
  compact receipt is still a baseline-safe object.
- **Invent a full privileged-log taxonomy now.** Rejected as too wide for this round.
- **Move all network receipts out too.** Rejected because transport/listener joins are still part of
  the bounded share story; the cut here is only about the stronger diagnostic/log lane.
