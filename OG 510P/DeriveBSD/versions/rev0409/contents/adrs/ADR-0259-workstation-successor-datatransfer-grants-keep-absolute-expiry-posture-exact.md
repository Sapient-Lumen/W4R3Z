# ADR-0259: Workstation successor data-transfer grants keep absolute expiry posture exact

Date: 2026-03-22  
Status: Accepted

## Context

`ADR-0252` made reviewed retry / re-offer continuity explicit through a fresh grant artifact plus `renewal_posture` and `supersedes_grant_digest`. `ADR-0253` narrowed that path to the same actor pair and same-or-narrower offer scope. `ADR-0254` narrowed it again so payload lineage and redaction posture stay exact when they are present. `ADR-0255` then made successor continuity exact-payload-bound, `ADR-0256` kept the foreground/interactivity requirement exact, `ADR-0257` kept delivery mode exact, and `ADR-0258` kept rate-limit posture exact too.

One more quiet timing-posture ambiguity still remained inside that already narrowed successor lane:
**can a reviewed successor keep the same actor pair, payload story, replay width, and throttling posture while still changing the outer absolute-expiry bound that explains why the grant must end when it does?**

Without a harder cut, an implementation could preserve familiar “allow again” wording while quietly adding, dropping, or swapping `constraints.expires_at`. Even if `effective_until` stayed acceptable for the moment, the same reviewed transfer story would now depend on a different outer deadline source than the one originally reviewed. That would push successor continuity back toward broker/policy folklore instead of the portable grant artifact.

## Decision

For the ordinary workstation lane:

1. `renewal_posture = supersedes-prior-grant` remains valid only for the **same reviewed transfer story**.
2. In addition to exact successor scope, payload lineage, redaction posture, exact payload binding, exact foreground posture, exact delivery mode, and exact rate-limit posture, successor continuity must also keep `constraints.expires_at` exact when present.
3. Compared with the predecessor named by `supersedes_grant_digest`, the successor must preserve presence/value parity for `constraints.expires_at`:
   - if the predecessor carried `constraints.expires_at`, the successor must also carry it,
   - if the predecessor omitted `constraints.expires_at`, the successor must also omit it,
   - and if both carry it, the timestamp must match exactly.
4. Add/drop/swap of `constraints.expires_at` is **fresh-grant required** even if the actor pair, offer scope, payload lineage, exact payload digest, foreground posture, delivery mode, rate-limit posture, and current `effective_until` all remain otherwise successor-shaped.
5. `effective_until` still stays the exact current grant deadline and must be no later than `constraints.expires_at` when present, but changing that outer absolute-expiry posture is not ordinary successor continuity.
6. Fresh issuance details may still change (`lease_id`, `offer.id`, `issued_at`, `effective_until`, signature`).

## Consequences

- “Allow again” now means the same reviewed outer absolute-expiry posture too, not merely the same payload story and execution posture.
- Detached support/export can explain whether a later grant still counted as the same reviewed transfer story without inferring whether the absolute expiry ceiling changed between grants.
- The ordinary workstation lane stays small: exact retry under the same absolute expiry posture may stay successor-shaped; extending, removing, or replacing the outer expiry ceiling goes back through fresh review.

## Alternatives considered

- **Allow successor retry to change `constraints.expires_at` if `effective_until` still looks okay:** rejected because it quietly changes the outer deadline semantics of the reviewed authority and would make continuity depend on hidden policy interpretation.
- **Treat `constraints.expires_at` as advisory metadata once `effective_until` exists:** rejected because the archive already uses it as an explicit upper-bound explanation and removing or swapping it would erase portable reasoning about why the deadline was what it was.
- **Collapse all timing posture into exact `effective_until` only and drop `constraints.expires_at`:** rejected for now because the archive already allows an explicit outer upper bound and some lanes may still need to explain that stronger source-bound/policy-bound deadline distinctly from the currently chosen grant deadline.

## Related

- `adrs/ADR-0251-workstation-datatransfer-grants-carry-exact-effective-until-and-late-delivery-fails-closed.md`
- `adrs/ADR-0252-workstation-datatransfer-renewals-stay-successor-grants-and-predecessor-digest-linked.md`
- `adrs/ADR-0253-workstation-successor-datatransfer-grants-stay-same-actor-pair-and-no-wider-offer.md`
- `adrs/ADR-0254-workstation-successor-datatransfer-grants-keep-payload-lineage-and-redaction-posture-exact.md`
- `adrs/ADR-0255-workstation-successor-datatransfer-grants-stay-exact-payload-bound-and-no-semantic-equivalence-rebinding.md`
- `adrs/ADR-0256-workstation-successor-datatransfer-grants-keep-foreground-requirement-exact.md`
- `adrs/ADR-0257-workstation-successor-datatransfer-grants-keep-delivery-mode-exact.md`
- `adrs/ADR-0258-workstation-successor-datatransfer-grants-keep-rate-limit-posture-exact.md`
- `docs/661-workstation-datatransfer-grants-carry-exact-effective-until-and-late-delivery-fails-closed.md`
- `docs/669-workstation-successor-datatransfer-grants-keep-absolute-expiry-posture-exact.md`
- `spec/ui.datatransfer.grant.schema.json`
