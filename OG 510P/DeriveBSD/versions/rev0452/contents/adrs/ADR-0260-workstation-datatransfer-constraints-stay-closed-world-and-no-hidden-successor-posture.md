# ADR-0260: Workstation data-transfer constraints stay closed-world and no hidden successor posture

Date: 2026-03-22  
Status: Accepted

## Context

`ADR-0252` made reviewed retry / re-offer continuity explicit through a fresh grant artifact plus `renewal_posture` and `supersedes_grant_digest`. `ADR-0253` narrowed that path to the same actor pair and same-or-narrower offer scope. `ADR-0254` kept payload lineage and redaction posture exact, `ADR-0255` kept the lane exact-payload-bound, `ADR-0256` kept foreground posture exact, `ADR-0257` kept delivery mode exact, `ADR-0258` kept rate-limit posture exact, and `ADR-0259` kept the outer absolute-expiry posture exact too.

One more quiet authority seam still remained inside that already narrowed successor lane:
**`ui.datatransfer.grant.constraints` was still open-world, so an implementation could keep all currently named successor-parity fields exact while quietly adding product-local or broker-local `constraints.*` keys that changed how the reviewed authority could be exercised.**

That would make the real successor contract depend on hidden per-implementation vocabulary instead of the portable grant artifact, and it would keep detached support/export from knowing whether “same reviewed transfer story” really exhausted the execution posture the archive meant to review.

## Decision

For the ordinary workstation data-transfer lane:

1. `ui.datatransfer.grant.constraints` is now a **closed-world typed vocabulary**.
2. The baseline artifact only admits the currently accepted typed keys: `requires_foreground`, `rate_limit`, and `expires_at`.
3. unknown or product-local extra `constraints.*` keys are **not baseline** for ordinary workstation transfer and are not allowed on the portable grant artifact.
4. Under `renewal_posture = supersedes-prior-grant`, there is therefore **no hidden successor execution posture** beyond the already accepted typed keys. If future execution posture is worth standardizing, it must come back through an ADR/spec change or a distinct richer transfer lane.
5. Fresh issuance details may still change (`lease_id`, `offer.id`, `issued_at`, `effective_until`, signature`), but hidden extra `constraints.*` vocabulary must not be used as the real contract.

## Consequences

- Portable tooling can treat `constraints` as a finite typed review surface instead of an open-ended bag of broker hints.
- Successor continuity stops at the already accepted typed posture keys; it no longer depends on implementation-private constraint names.
- Future richer transfer posture is still possible, but it must be made explicit through spec evolution instead of sneaking back in as arbitrary `constraints.*` drift.

## Alternatives considered

- **Keep `constraints` open-world and continue freezing fields one by one:** rejected because it leaves hidden extra posture available by default and keeps the portable contract under-specified.
- **Add a digest over an otherwise open-world `constraints` bag:** rejected for now because it would preserve opaque vocabulary rather than forcing the archive to name and justify new authority surface explicitly.
- **Allow profile- or product-local `constraints.*` extensions in the ordinary lane:** rejected because that would make A/B/C/D portability and support/export reasoning depend on local folklore instead of one shared artifact contract.

## Related

- `adrs/ADR-0252-workstation-datatransfer-renewals-stay-successor-grants-and-predecessor-digest-linked.md`
- `adrs/ADR-0253-workstation-successor-datatransfer-grants-stay-same-actor-pair-and-no-wider-offer.md`
- `adrs/ADR-0254-workstation-successor-datatransfer-grants-keep-payload-lineage-and-redaction-posture-exact.md`
- `adrs/ADR-0255-workstation-successor-datatransfer-grants-stay-exact-payload-bound-and-no-semantic-equivalence-rebinding.md`
- `adrs/ADR-0256-workstation-successor-datatransfer-grants-keep-foreground-requirement-exact.md`
- `adrs/ADR-0257-workstation-successor-datatransfer-grants-keep-delivery-mode-exact.md`
- `adrs/ADR-0258-workstation-successor-datatransfer-grants-keep-rate-limit-posture-exact.md`
- `adrs/ADR-0259-workstation-successor-datatransfer-grants-keep-absolute-expiry-posture-exact.md`
- `docs/670-workstation-datatransfer-constraints-stay-closed-world-and-no-hidden-successor-posture.md`
- `spec/ui.datatransfer.grant.schema.json`
