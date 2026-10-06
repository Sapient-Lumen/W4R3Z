# ADR-0123: hardware support qualification status boundary

Date: 2026-03-17
Status: Accepted

## Context

`adrs/ADR-0118-hardware-support-matrix-and-bundled-admission-boundary.md` fixed where support claims live: `hw.support.matrix` is the digest-bound catalog artifact.
`adrs/ADR-0119-hardware-support-promotion-and-qualification-boundary.md` fixed that positive entries must carry a typed `qualification` summary.
`adrs/ADR-0120-hardware-support-qualification-receipt-boundary.md` fixed that the summary must point at a typed `hw.support.qualification.receipt`.
`adrs/ADR-0121-hardware-support-qualification-profile-boundary.md` fixed that receipts must point at a typed `hw.support.qualification.profile`.
`adrs/ADR-0122-hardware-support-qualification-freshness-boundary.md` fixed that the standard and receipt must also carry typed freshness.

That still left one small but expensive ambiguity: the receipt schema already allowed `decision.status = accepted | superseded | revoked`, but the archive never said what those statuses actually do to a positive support claim.
Without that boundary, `superseded` and `revoked` are just interesting words in a schema while support bundles and preflight still act as if the matched proof were current.

Real ecosystems do not treat old qualification evidence as timeless. Android requires full CTS for final production builds and expects failures to be fixed before release. Ubuntu positions certified hardware as continuously tested through the release lifecycle. Windows qualification stays tied to the current official HLK compatibility playlists rather than a forever-valid past pass.

## Decision

Accept a typed lifecycle boundary for hardware support qualification receipts.

1. **Positive support claims must point at an `accepted` receipt.**
   `hw.support.matrix.entries[].qualification.receipt_digest` is only valid for current positive publication when the referenced `hw.support.qualification.receipt.decision.status` is `accepted`.

2. **Receipt status is now operational, not decorative.**
   `hw.support.qualification.receipt.decision` must carry `status_effective_at`.
   - `accepted` means the receipt may back a current positive support claim.
   - `superseded` means the receipt is historical only and must carry `replacement_receipt_digest` plus `reason_code = newer-receipt-published`.
   - `revoked` means the receipt must not back a positive support claim and must carry a typed `reason_code`.

3. **Preflight/reporting gets explicit non-current findings.**
   `hw.compat.report` may now emit `qualification-superseded` or `qualification-revoked` when a matched support claim points at a receipt that is no longer current. These findings are distinct from `qualification-stale`: stale means the proof aged out; superseded/revoked means publication state explicitly changed.

4. **The matrix stays a release snapshot, not a live advisory service.**
   If a receipt is later superseded or revoked, the next published matrix/bundle/release train must update the referenced receipt digest, downgrade the entry, or remove the positive claim. Old artifacts remain historical evidence; they do not become a live support portal.

## Consequences

Good:
- B/workstation consent can distinguish “this support proof is old” from “this support proof has been actively withdrawn or replaced.”
- D/appliance bundles can carry a durable explanation for why a support claim stopped counting without inventing a live certification backend.
- A/fleet rollouts stop conflating past qualification with current support publication.
- The existing receipt lifecycle fields become meaningful enough to implement against.

Trade-offs:
- The support lane gains one more small vocabulary surface (`reason_code` and new report findings).
- The archive still does not define a universal notification service or automated recertification pipeline.

## Follow-up

This ADR does **not** decide:
- the final trusted-UI wording for `qualification-superseded` or `qualification-revoked`,
- the full automation story for discovering field regressions and publishing replacement receipts,
- or how broad release-notification fanout should become.

It only fixes the lifecycle boundary so support qualification status is typed, explainable, and mechanically joinable from the existing matrix/report lane.
