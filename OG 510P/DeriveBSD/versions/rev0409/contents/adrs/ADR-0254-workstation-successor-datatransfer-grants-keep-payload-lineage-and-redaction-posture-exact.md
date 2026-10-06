# ADR-0254: Workstation successor data-transfer grants keep payload lineage and redaction posture exact

Date: 2026-03-22  
Status: Accepted

## Context

`ADR-0252` made reviewed retry / re-offer continuity explicit through a fresh grant artifact plus `renewal_posture` and `supersedes_grant_digest`. `ADR-0253` then narrowed that successor path further: reviewed successor grants are only for the same actor pair and the same-or-narrower typed offer envelope.

One more quiet ambiguity remained inside that narrowed envelope:
**can a successor retry keep the same app pair and MIME/byte bounds while still silently changing which payload lineage or redaction posture is crossing?**

Without a harder cut, an implementation could preserve familiar “allow again” wording while swapping to a different `content_source` lineage, dropping provenance that existed on the predecessor, or changing `redaction_profile_digest` under the old transfer story. That would make successor continuity depend on hidden broker/UI state instead of the grant artifact itself.

## Decision

For the ordinary workstation lane:

1. `renewal_posture = supersedes-prior-grant` remains valid only for the **same reviewed transfer story**.
2. In addition to `successor_scope_posture = same-actor-pair-and-no-wider-offer`, successor continuity must also keep payload lineage and redaction posture exact.
3. Compared with the predecessor named by `supersedes_grant_digest`:
   - if `offer.content_source` is present, the successor must carry the exact same `offer.content_source` object,
   - if `offer.content_source` is absent, the successor must also leave it absent,
   - if `offer.redaction_profile_digest` is present, the successor must carry the exact same digest,
   - if `offer.redaction_profile_digest` is absent, the successor must also leave it absent.
4. Add/drop/swap of either field is **fresh-grant required**, even if actor pair, direction, and MIME/byte bounds remain successor-shaped.
5. Fresh issuance details may still change (`lease_id`, `offer.id`, `issued_at`, `effective_until`, signature, and other newly minted artifact identity).

## Consequences

- “Allow again” now means *the same reviewed transfer story* more precisely, not merely the same apps and same outer MIME envelope.
- Detached support/export can explain continuity without reopening broker databases or trusted-UI state.
- OCR/searchable follow-on flows that rely on `content_source` lineage stay auditable instead of becoming clipboard folklore.

## Alternatives considered

- **Allow successor continuity to change lineage/redaction as long as MIME/bytes stay inside predecessor bounds:** rejected because payload provenance and redaction posture materially affect what authority is being exercised.
- **Infer same-story payload continuity from `offer.id`, broker history, or UI phrasing:** rejected because that weakens detached verification and recreates local-state folklore.
- **Design a richer multi-payload transfer family now:** rejected as too large for this iteration; the smaller useful cut is to keep successor continuity exact and push changed payload posture back onto the fresh-grant lane.

## Related

- `adrs/ADR-0252-workstation-datatransfer-renewals-stay-successor-grants-and-predecessor-digest-linked.md`
- `adrs/ADR-0253-workstation-successor-datatransfer-grants-stay-same-actor-pair-and-no-wider-offer.md`
- `docs/657-workstation-ocr-text-egress-stays-explicit-plain-text-single-delivery.md`
- `docs/663-workstation-successor-datatransfer-grants-stay-same-actor-pair-and-no-wider-offer.md`
- `docs/664-workstation-successor-datatransfer-grants-keep-payload-lineage-and-redaction-posture-exact.md`
- `spec/ui.datatransfer.grant.schema.json`
