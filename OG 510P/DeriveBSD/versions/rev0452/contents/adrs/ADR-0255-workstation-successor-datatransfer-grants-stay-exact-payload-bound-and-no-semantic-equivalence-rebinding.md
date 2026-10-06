# ADR-0255: Workstation successor data-transfer grants stay exact-payload-bound and no semantic-equivalence rebinding

Date: 2026-03-22  
Status: Accepted

## Context

`ADR-0252` made reviewed retry / re-offer continuity explicit through a fresh grant artifact plus `renewal_posture` and `supersedes_grant_digest`. `ADR-0253` narrowed that path to the same actor pair and same-or-narrower offer scope. `ADR-0254` narrowed it again so payload lineage and redaction posture stay exact when they are present.

One more quiet ambiguity remained inside that already narrowed successor lane:
**can a reviewed successor keep the same actor pair, envelope, payload lineage, and redaction posture while still rebinding to newly rendered or semantically equivalent payload bytes?**

Without a harder cut, an implementation could preserve familiar “allow again” wording while quietly re-rendering a secret, re-serializing the payload with different bytes, or substituting a look-alike clipboard value under the old transfer story. That would make successor continuity depend on broker/UI memory about what “really counted as the same thing” instead of a portable artifact boundary.

## Decision

For the ordinary workstation lane:

1. `renewal_posture = supersedes-prior-grant` remains valid only for the **same reviewed transfer story**.
2. In addition to `successor_scope_posture = same-actor-pair-and-no-wider-offer` and exact `offer.content_source` / `offer.redaction_profile_digest` parity, successor continuity is also **exact-payload-bound**.
3. `ui.datatransfer.grant.offer.payload_digest` is the portable digest of the exact offered payload for that reviewed transfer story.
4. Compared with the predecessor named by `supersedes_grant_digest`:
   - the successor must carry `offer.payload_digest`,
   - the predecessor must also have carried `offer.payload_digest`,
   - and the successor value must be exactly equal to the predecessor value.
5. If an implementation wants to retry with newly rendered, re-serialized, semantically equivalent, or otherwise substituted bytes, that act is **fresh-grant required**.
6. `ui.datatransfer.receipt.summary.payload_digest` should echo the exact transferred payload digest so detached support/export can verify that the delivered bytes matched the reviewed grant story.

## Consequences

- “Allow again” now means the same reviewed payload, not merely the same apps, scope, lineage hints, or redaction story.
- Detached support/export can explain successor continuity without reopening clipboard-manager state or broker notes about semantic equivalence.
- The ordinary workstation lane remains small: exact replay of the same reviewed payload can stay successor-shaped; anything else goes back through fresh review.

## Alternatives considered

- **Allow semantically equivalent or re-rendered payloads on the successor lane:** rejected because “equivalent enough” is not a portable authority boundary and would recreate hidden broker-policy folklore.
- **Infer exact payload continuity from `offer.id`, UI wording, or broker history:** rejected because those are operational correlates, not portable evidence of the exact reviewed payload.
- **Require every ordinary transfer to predeclare a richer multi-representation canonicalization family now:** rejected as too large for this iteration; the smaller useful cut is a digest for the exact reviewed payload story and a fail-closed rule for substitution.

## Related

- `adrs/ADR-0252-workstation-datatransfer-renewals-stay-successor-grants-and-predecessor-digest-linked.md`
- `adrs/ADR-0253-workstation-successor-datatransfer-grants-stay-same-actor-pair-and-no-wider-offer.md`
- `adrs/ADR-0254-workstation-successor-datatransfer-grants-keep-payload-lineage-and-redaction-posture-exact.md`
- `docs/657-workstation-ocr-text-egress-stays-explicit-plain-text-single-delivery.md`
- `docs/664-workstation-successor-datatransfer-grants-keep-payload-lineage-and-redaction-posture-exact.md`
- `docs/665-workstation-successor-datatransfer-grants-stay-exact-payload-bound-and-no-semantic-equivalence-rebinding.md`
- `spec/ui.datatransfer.grant.schema.json`
- `spec/ui.datatransfer.receipt.schema.json`
