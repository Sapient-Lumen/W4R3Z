# ADR-0257: Workstation successor data-transfer grants keep delivery mode exact

Date: 2026-03-22  
Status: Accepted

## Context

`ADR-0252` made reviewed retry / re-offer continuity explicit through a fresh grant artifact plus `renewal_posture` and `supersedes_grant_digest`. `ADR-0253` narrowed that path to the same actor pair and same-or-narrower offer scope. `ADR-0254` narrowed it again so payload lineage and redaction posture stay exact when they are present. `ADR-0255` then made successor continuity exact-payload-bound, and `ADR-0256` kept the foreground/interactivity requirement exact.

One more quiet ambiguity remained inside that already narrowed successor lane:
**can a reviewed successor keep the same actor pair, payload story, and foreground posture while still changing how many deliveries the authority allows?**

Without a harder cut, an implementation could preserve familiar “allow again” wording while quietly changing `delivery_mode` from the ordinary one-shot lane to an explicit multi-delivery exception lane. That would let broader replay/reuse authority inherit an approval that was reviewed as single-delivery, and it would make successor continuity depend on broker-side convenience behavior instead of the portable grant artifact.

## Decision

For the ordinary workstation lane:

1. `renewal_posture = supersedes-prior-grant` remains valid only for the **same reviewed transfer story**.
2. In addition to exact successor scope, payload lineage, redaction posture, exact payload binding, and exact foreground posture, successor continuity must also keep `delivery_mode` exact.
3. Compared with the predecessor named by `supersedes_grant_digest`, the successor must carry the same `delivery_mode` value.
4. In particular, a predecessor reviewed as `single-delivery` must not quietly become `multi-delivery` under successor continuity.
5. Any add/drop/swap of delivery semantics is **fresh-grant required** even if the actor pair, offer scope, payload lineage, exact payload digest, and foreground posture remain successor-shaped.
6. Fresh issuance details may still change (`lease_id`, `offer.id`, `issued_at`, `effective_until`, signature).

## Consequences

- “Allow again” now means the same reviewed delivery semantics too, not merely the same payload story.
- Detached support/export can explain why a later grant still counted as the same reviewed transfer story without inferring whether replay/reuse authority widened between grants.
- The ordinary workstation lane stays small: exact retry of the same reviewed delivery mode may stay successor-shaped; switching to or from a multi-delivery lane goes back through fresh review.

## Alternatives considered

- **Allow successor retry to widen from `single-delivery` to `multi-delivery` when everything else stays the same:** rejected because it quietly changes how many times the reviewed authority may be exercised and would let replay/reuse authority inherit approval that was reviewed as one-shot.
- **Infer successor delivery semantics from current broker policy or lease state:** rejected because broker policy and lease state are operational conditions, not portable evidence of what the reviewed grant authorized.
- **Fully specify the multi-delivery exception lane now:** rejected as too large for this iteration; the smallest useful cut is to prevent successor continuity from silently becoming that wider lane.

## Related

- `adrs/ADR-0252-workstation-datatransfer-renewals-stay-successor-grants-and-predecessor-digest-linked.md`
- `adrs/ADR-0253-workstation-successor-datatransfer-grants-stay-same-actor-pair-and-no-wider-offer.md`
- `adrs/ADR-0254-workstation-successor-datatransfer-grants-keep-payload-lineage-and-redaction-posture-exact.md`
- `adrs/ADR-0255-workstation-successor-datatransfer-grants-stay-exact-payload-bound-and-no-semantic-equivalence-rebinding.md`
- `adrs/ADR-0256-workstation-successor-datatransfer-grants-keep-foreground-requirement-exact.md`
- `docs/660-workstation-single-delivery-datatransfer-grants-stay-one-shot-and-fresh-grant-required.md`
- `docs/666-workstation-successor-datatransfer-grants-keep-foreground-requirement-exact.md`
- `docs/667-workstation-successor-datatransfer-grants-keep-delivery-mode-exact.md`
- `spec/ui.datatransfer.grant.schema.json`
