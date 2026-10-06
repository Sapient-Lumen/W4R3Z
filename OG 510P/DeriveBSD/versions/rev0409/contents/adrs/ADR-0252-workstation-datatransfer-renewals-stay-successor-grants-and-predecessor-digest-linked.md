# ADR-0252: Workstation data-transfer renewals stay successor grants and predecessor-digest linked

- Status: Accepted
- Date: 2026-03-22

## Context

`adrs/ADR-0250-workstation-single-delivery-datatransfer-grants-stay-one-shot-and-fresh-grant-required.md` already fixed the ordinary workstation recovery posture after success: the first successful read-side transfer exhausts the grant, and later recovery is a fresh explicit grant / re-offer required. `ADR-0251` then fixed the other terminal edge by making `effective_until` exact and late delivery fail closed.

That still left one more portability gap:
**when a human or policy reviews “allow again”, “copy again”, or a retry after expiry/exhaustion, what keeps that act from becoming an in-place broker row update instead of a new reviewed grant artifact?**

If the archive does not choose, implementations drift toward:
- extending the old grant deadline in place,
- reusing an old grant digest while changing timing or state behind the scenes,
- or inferring continuity from `offer.id`, `lease_id`, or “same source/destination pair” folklore.

## Decision

1. `ui.datatransfer.grant` now requires `renewal_posture`.
2. `renewal_posture = fresh-grant` means the grant starts a new reviewed transfer story.
3. `renewal_posture = supersedes-prior-grant` means the grant is a reviewed successor to an earlier transfer grant.
4. If `renewal_posture = supersedes-prior-grant`, the grant must carry `supersedes_grant_digest` naming the exact prior `ui.datatransfer.grant` digest it replaces.
5. Renewal/re-offer stays **new artifact plus predecessor digest**, not in-place extension of an older grant.
6. `offer.id`, `lease_id`, timestamps, or subject overlap may remain useful operational correlates, but they are not the portable source of truth for renewal continuity.

## Consequences

- “Allow again” / retry UX must mint a fresh reviewed grant artifact when it continues an earlier transfer story.
- Detached support/export can now answer not only which exact grant was consumed (`grant_digest`), but also whether that grant started a new story or explicitly superseded an earlier grant.
- Implementations lose some shortcut freedom because extending an old grant in place is no longer the boring answer.

## Alternatives considered

- **Keep fresh grant / re-offer language only in prose:** too easy for implementations to hide the real continuity rule in broker state.
- **Infer renewal from `offer.id` / `lease_id` reuse:** too much backend folklore and not portable.
- **Design a bigger replay/retry subsystem first:** too large for this iteration; the smaller useful cut is to make reviewed successor lineage explicit on the grant artifact itself.

## References

- `adrs/ADR-0128-workstation-cross-domain-datatransfer-floor.md`
- `adrs/ADR-0249-workstation-datatransfer-receipts-join-exact-grants-by-digest.md`
- `adrs/ADR-0250-workstation-single-delivery-datatransfer-grants-stay-one-shot-and-fresh-grant-required.md`
- `adrs/ADR-0251-workstation-datatransfer-grants-carry-exact-effective-until-and-late-delivery-fails-closed.md`
- `docs/205-data-transfer-portals-clipboard-and-dnd.md`
- `docs/538-workstation-cross-domain-datatransfer-floor.md`
- `docs/660-workstation-single-delivery-datatransfer-grants-stay-one-shot-and-fresh-grant-required.md`
- `docs/661-workstation-datatransfer-grants-carry-exact-effective-until-and-late-delivery-fails-closed.md`
- `docs/662-workstation-datatransfer-renewals-stay-successor-grants-and-predecessor-digest-linked.md`
- `spec/ui.datatransfer.grant.schema.json`
