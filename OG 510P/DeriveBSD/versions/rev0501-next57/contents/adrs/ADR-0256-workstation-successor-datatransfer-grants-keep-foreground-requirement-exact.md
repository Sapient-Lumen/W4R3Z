# ADR-0256: Workstation successor data-transfer grants keep foreground requirement exact

Date: 2026-03-22  
Status: Accepted

## Context

`ADR-0252` made reviewed retry / re-offer continuity explicit through a fresh grant artifact plus `renewal_posture` and `supersedes_grant_digest`. `ADR-0253` narrowed that path to the same actor pair and same-or-narrower offer scope. `ADR-0254` narrowed it again so payload lineage and redaction posture stay exact when they are present. `ADR-0255` then made successor continuity exact-payload-bound.

One more quiet ambiguity remained inside that already narrowed successor lane:
**can a reviewed successor keep the same actor pair, envelope, lineage, and exact payload while still changing the transfer from foreground-required to background-capable?**

Without a harder cut, an implementation could preserve familiar “allow again” wording while quietly dropping the foreground requirement, allowing a later broker or destination to consume the same reviewed payload without the same trusted-UI visibility that governed the earlier approval. That would make successor continuity depend on host-local broker behavior and human expectation instead of the portable grant artifact.

## Decision

For the ordinary workstation lane:

1. `renewal_posture = supersedes-prior-grant` remains valid only for the **same reviewed transfer story**.
2. In addition to exact successor scope, payload lineage, redaction posture, and exact payload binding, successor continuity must also keep the foreground/interactivity posture exact.
3. `ui.datatransfer.grant.constraints.requires_foreground` is the portable foreground requirement when present.
4. Compared with the predecessor named by `supersedes_grant_digest`:
   - if the predecessor carried `constraints.requires_foreground`, the successor must also carry it,
   - if the predecessor omitted `constraints.requires_foreground`, the successor must also omit it,
   - and when present the successor value must be exactly equal to the predecessor value.
5. Add/drop/swap of `constraints.requires_foreground` is **fresh-grant required** even if the actor pair, offer scope, payload lineage, and exact payload digest remain successor-shaped.
6. Fresh issuance details may still change (`lease_id`, `offer.id`, `issued_at`, `effective_until`, signature).

## Consequences

- “Allow again” now means the same reviewed interactivity posture too, not merely the same payload story.
- Detached support/export can explain why a later grant still counted as the same reviewed transfer story without reopening trusted-UI screenshots or broker notes.
- The ordinary workstation lane stays small: exact retry of the same reviewed foreground posture may stay successor-shaped; relaxing or tightening foreground visibility goes back through fresh review.

## Alternatives considered

- **Allow successor retry to drop the foreground requirement when payload and scope stay the same:** rejected because it silently changes how authority is exercised and would let background-capable delivery inherit an approval that was reviewed as foreground-visible.
- **Infer foreground continuity from current focus state or broker policy:** rejected because focus state and broker policy are operational conditions, not portable evidence of what the reviewed grant authorized.
- **Freeze every transfer constraint now, including rate-limit and every future policy hint:** rejected as too large for this iteration; the smallest useful cut is the foreground requirement because it materially changes trusted-UI visibility and backgroundability.

## Related

- `adrs/ADR-0252-workstation-datatransfer-renewals-stay-successor-grants-and-predecessor-digest-linked.md`
- `adrs/ADR-0253-workstation-successor-datatransfer-grants-stay-same-actor-pair-and-no-wider-offer.md`
- `adrs/ADR-0254-workstation-successor-datatransfer-grants-keep-payload-lineage-and-redaction-posture-exact.md`
- `adrs/ADR-0255-workstation-successor-datatransfer-grants-stay-exact-payload-bound-and-no-semantic-equivalence-rebinding.md`
- `docs/665-workstation-successor-datatransfer-grants-stay-exact-payload-bound-and-no-semantic-equivalence-rebinding.md`
- `docs/666-workstation-successor-datatransfer-grants-keep-foreground-requirement-exact.md`
- `spec/ui.datatransfer.grant.schema.json`
