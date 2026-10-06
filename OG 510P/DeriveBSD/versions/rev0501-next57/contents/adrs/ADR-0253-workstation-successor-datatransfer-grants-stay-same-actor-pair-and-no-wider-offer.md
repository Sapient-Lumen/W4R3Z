# ADR-0253: Workstation successor data-transfer grants stay same-actor-pair and no-wider-offer

Date: 2026-03-22  
Status: Accepted

## Context

`adrs/ADR-0250-workstation-single-delivery-datatransfer-grants-stay-one-shot-and-fresh-grant-required.md` already fixed the ordinary workstation recovery posture after success: the first successful read-side transfer exhausts the grant and later recovery is a fresh explicit grant / re-offer required. `ADR-0251` then made ordinary grant lifetime exact through `effective_until`, and `ADR-0252` made reviewed retry/re-offer successor-shaped through `renewal_posture` plus `supersedes_grant_digest`.

One narrower but still expensive ambiguity remained:
**once a reviewed retry is allowed to name a predecessor, what keeps that successor-shaped path from quietly widening the transfer instead of simply renewing the same reviewed transfer story?**

Without a tighter cut, an implementation could reuse successor language while also changing source/destination, adding broader MIME types, increasing `max_bytes`, or otherwise expanding the practical scope of the crossing. That would turn "successor grant" into a stealth authority-escalation lane.

## Decision

For the ordinary workstation lane:

1. `renewal_posture = supersedes-prior-grant` is only valid for the **same reviewed transfer story**, not for a broadened transfer.
2. Successor grants must therefore carry `successor_scope_posture` = `same-actor-pair-and-no-wider-offer`.
3. Compared with the predecessor named by `supersedes_grant_digest`, the successor grant must keep the same `subject`, `offer_source_subject`, `direction`, and `delivery_mode`.
4. Compared with that predecessor, the successor offer must stay the same or narrower on the currently typed offer envelope:
   - `offer.mime_types` must stay equal or become a subset,
   - `offer.max_bytes` must stay equal or smaller, and
   - when `offer.redaction_profile_digest` and/or `offer.content_source` are present, they must not silently switch to a different value under successor continuity.
5. Fresh issuance details may change (`lease_id`, `offer.id`, `issued_at`, `effective_until`, signature, and other newly minted artifact identity), and the successor may narrow the offer.
6. Any actor-pair change or broader offer change is **fresh-grant required**, even if the trusted UI wording says "allow again" or the broker thinks the retry is related.

## Consequences

- Reviewed retry stays useful without becoming an implicit widening lane.
- Detached tooling can distinguish "renewed same story" from "new broader transfer" without trusting trusted-UI wording.
- Future richer retry/escalation lanes remain possible, but they now need an explicit fresh-grant or separate exception design instead of piggybacking on successor continuity.

## Alternatives considered

- **Allow successor grants to widen scope if the same app pair is involved:** rejected because actor continuity alone is too weak; it still hides real authority expansion behind retry wording.
- **Infer same-story scope from `offer.id` / `lease_id` / recency:** rejected because that recreates broker-memory folklore and makes detached support/export weaker.
- **Design a full widening/escalation subsystem now:** rejected as too large for this iteration; the smaller useful cut is to keep successor continuity narrow and push wider changes back onto fresh reviewed grants.

## Related

- `adrs/ADR-0128-workstation-cross-domain-datatransfer-floor.md`
- `adrs/ADR-0249-workstation-datatransfer-receipts-join-exact-grants-by-digest.md`
- `adrs/ADR-0250-workstation-single-delivery-datatransfer-grants-stay-one-shot-and-fresh-grant-required.md`
- `adrs/ADR-0251-workstation-datatransfer-grants-carry-exact-effective-until-and-late-delivery-fails-closed.md`
- `adrs/ADR-0252-workstation-datatransfer-renewals-stay-successor-grants-and-predecessor-digest-linked.md`
- `docs/663-workstation-successor-datatransfer-grants-stay-same-actor-pair-and-no-wider-offer.md`
- `spec/ui.datatransfer.grant.schema.json`
