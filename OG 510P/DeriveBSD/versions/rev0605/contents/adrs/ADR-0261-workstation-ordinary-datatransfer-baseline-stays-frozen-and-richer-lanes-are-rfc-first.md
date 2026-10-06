# ADR-0261: Workstation ordinary data-transfer baseline stays frozen and richer lanes are RFC-first

Date: 2026-03-22  
Status: Accepted

## Context

`ADR-0252` through `ADR-0260` progressively narrowed the ordinary workstation `ui.datatransfer.grant` lane until the portable contract now has explicit successor lineage, same-actor-pair and no-wider-offer scope, exact payload lineage/redaction posture, exact payload digest, exact foreground posture, exact delivery mode, exact rate-limit posture, exact absolute-expiry posture, and a closed-world typed `constraints` vocabulary.

That sequence paid down a large amount of ambiguity, but it also exposed the next archive-management risk:
**if we keep treating the ordinary portable lane as indefinitely expandable, the archive can continue accreting richer transfer ideas through small local edits instead of admitting when a distinct richer lane deserves its own design pass.**

At this point the ordinary portable lane is coherent enough to implement. The next questions—batched/replay-friendly review lanes, broader substitution rules, richer directory-like or collection-like transfer authority, or other widened transfer posture—are no longer baseline tightening. They are design expansions.

## Decision

For the ordinary workstation transfer lane:

1. the ordinary `ui.datatransfer.grant` artifact family is now the **frozen portable baseline** for workstation reviewable transfer.
2. this ordinary portable baseline is treated as **complete enough to implement**.
3. future richer replay/batching, widened/substituting, collection-like, or otherwise broader transfer lanes are **RFC-first** and must not grow by quiet schema extension, successor-path wording drift, or broker-local convention.
4. such richer ideas are therefore **not baseline** until the archive accepts a separate RFC/ADR-backed lane.
5. the ordinary lane may still receive bug fixes, clarification, and coherence work, but not quiet authority growth.

## Consequences

- The workstation archive stops paying entropy costs on “one more small widening” of the same ordinary transfer artifact family.
- Implementation work can now target a stable ordinary reviewed-transfer floor instead of a moving baseline.
- If practice later forces a richer lane, it will arrive with explicit profile/tier justification rather than silently colonizing the portable baseline.

## Alternatives considered

- **Keep narrowing the ordinary lane one field at a time forever:** rejected because it obscures when the work has shifted from baseline clarification into new-lane design.
- **Start designing a richer lane immediately inside the baseline artifacts:** rejected because no single richer lane has yet earned priority strongly enough to justify widening the ordinary portable contract now.
- **Leave the boundary implicit:** rejected because archive drift returns unless the stop-point is stated plainly and guarded.

## Related

- `adrs/ADR-0252-workstation-datatransfer-renewals-stay-successor-grants-and-predecessor-digest-linked.md`
- `adrs/ADR-0253-workstation-successor-datatransfer-grants-stay-same-actor-pair-and-no-wider-offer.md`
- `adrs/ADR-0254-workstation-successor-datatransfer-grants-keep-payload-lineage-and-redaction-posture-exact.md`
- `adrs/ADR-0255-workstation-successor-datatransfer-grants-stay-exact-payload-bound-and-no-semantic-equivalence-rebinding.md`
- `adrs/ADR-0256-workstation-successor-datatransfer-grants-keep-foreground-requirement-exact.md`
- `adrs/ADR-0257-workstation-successor-datatransfer-grants-keep-delivery-mode-exact.md`
- `adrs/ADR-0258-workstation-successor-datatransfer-grants-keep-rate-limit-posture-exact.md`
- `adrs/ADR-0259-workstation-successor-datatransfer-grants-keep-absolute-expiry-posture-exact.md`
- `adrs/ADR-0260-workstation-datatransfer-constraints-stay-closed-world-and-no-hidden-successor-posture.md`
- `docs/671-workstation-ordinary-datatransfer-baseline-stays-frozen-and-richer-lanes-are-rfc-first.md`
- `spec/ui.datatransfer.grant.schema.json`
