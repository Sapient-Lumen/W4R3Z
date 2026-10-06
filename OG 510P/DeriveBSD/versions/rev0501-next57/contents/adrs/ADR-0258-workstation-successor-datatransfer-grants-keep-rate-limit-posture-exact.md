# ADR-0258: Workstation successor data-transfer grants keep rate-limit posture exact

Date: 2026-03-22  
Status: Accepted

## Context

`ADR-0252` made reviewed retry / re-offer continuity explicit through a fresh grant artifact plus `renewal_posture` and `supersedes_grant_digest`. `ADR-0253` narrowed that path to the same actor pair and same-or-narrower offer scope. `ADR-0254` narrowed it again so payload lineage and redaction posture stay exact when they are present. `ADR-0255` then made successor continuity exact-payload-bound, `ADR-0256` kept the foreground/interactivity requirement exact, and `ADR-0257` kept delivery mode exact too.

One more quiet execution-posture ambiguity remained inside that already narrowed successor lane:
**can a reviewed successor keep the same actor pair, payload story, foreground posture, and delivery mode while still changing how fast or how bursty the authority may be exercised?**

Without a harder cut, an implementation could preserve familiar “allow again” wording while quietly changing `constraints.rate_limit`. That would let the same reviewed transfer story inherit a different tempo/throughput posture than the one originally reviewed, and it would make successor continuity depend on broker-side throttling policy instead of the portable grant artifact.

## Decision

For the ordinary workstation lane:

1. `renewal_posture = supersedes-prior-grant` remains valid only for the **same reviewed transfer story**.
2. In addition to exact successor scope, payload lineage, redaction posture, exact payload binding, exact foreground posture, and exact delivery mode, successor continuity must also keep `constraints.rate_limit` exact when present.
3. Compared with the predecessor named by `supersedes_grant_digest`, the successor must preserve presence/value parity for `constraints.rate_limit`:
   - if the predecessor carried `constraints.rate_limit`, the successor must also carry it,
   - if the predecessor omitted `constraints.rate_limit`, the successor must also omit it,
   - and if both carry it, the string value must match exactly.
4. Add/drop/swap of `constraints.rate_limit` is **fresh-grant required** even if the actor pair, offer scope, payload lineage, exact payload digest, foreground posture, and delivery mode remain successor-shaped.
5. Fresh issuance details may still change (`lease_id`, `offer.id`, `issued_at`, `effective_until`, `signature`).

## Consequences

- “Allow again” now means the same reviewed throughput/tempo posture too, not merely the same payload story and replay width.
- Detached support/export can explain why a later grant still counted as the same reviewed transfer story without inferring whether throttling semantics widened or tightened between grants.
- The ordinary workstation lane stays small: exact retry of the same reviewed rate-limit posture may stay successor-shaped; changing the rate/tempo of transfer authority goes back through fresh review.

## Alternatives considered

- **Allow successor retry to change `constraints.rate_limit` when everything else stays the same:** rejected because it quietly changes how the reviewed authority may be exercised over time and would push the real contract back into broker-side throttling policy.
- **Infer successor throttling semantics from current broker policy or lease state:** rejected because broker policy and lease state are operational conditions, not portable evidence of what the reviewed grant authorized.
- **Fully specify all richer throttling/multi-delivery exception lanes now:** rejected as too large for this iteration; the smallest useful cut is to prevent successor continuity from silently becoming that different execution-tempo lane.

## Related

- `adrs/ADR-0252-workstation-datatransfer-renewals-stay-successor-grants-and-predecessor-digest-linked.md`
- `adrs/ADR-0253-workstation-successor-datatransfer-grants-stay-same-actor-pair-and-no-wider-offer.md`
- `adrs/ADR-0254-workstation-successor-datatransfer-grants-keep-payload-lineage-and-redaction-posture-exact.md`
- `adrs/ADR-0255-workstation-successor-datatransfer-grants-stay-exact-payload-bound-and-no-semantic-equivalence-rebinding.md`
- `adrs/ADR-0256-workstation-successor-datatransfer-grants-keep-foreground-requirement-exact.md`
- `adrs/ADR-0257-workstation-successor-datatransfer-grants-keep-delivery-mode-exact.md`
- `docs/666-workstation-successor-datatransfer-grants-keep-foreground-requirement-exact.md`
- `docs/667-workstation-successor-datatransfer-grants-keep-delivery-mode-exact.md`
- `docs/668-workstation-successor-datatransfer-grants-keep-rate-limit-posture-exact.md`
- `spec/ui.datatransfer.grant.schema.json`
