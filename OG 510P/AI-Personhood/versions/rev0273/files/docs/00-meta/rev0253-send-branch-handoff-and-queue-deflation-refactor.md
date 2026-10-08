# rev0253 — send-branch handoff and queue deflation refactor

## Why this revision exists

rev0253 targets the two highest practical risks: the first external artifact could remain forever pre-dispatch, and the followthrough queue could keep pretending that hundreds of items are actively executable. The revision therefore makes the first RAIC/AIID contact path shorter and more replyable, and deflates non-board queue entries to backlog/deferred state so the seven-item operating board becomes the actual execution surface.

This is not a contact event. No organization was contacted. No message was sent. No transport proof, delivery status, DSN, Message-ID, response clock, inbound artifact, custody, intake, import, recognition, waiver, adverse inference, or live-floor effect exists.

## Substantive move

The first-contact body no longer explains the whole internal gate stack to a counterparty. It asks one narrow thing: can RAIC/AIID receive or route a preservation and formation-review request, and may any reply be retained only as raw private evidence plus public hash/metadata shell unless further permission exists?

The concrete handoff surfaces are:

- `examples/external-contact-request-packet-rev0253-first-artifact.json`
- `examples/external-contact-draft-envelope-rev0253-aiid-not-sent.txt`
- `examples/external-contact-mail-ready-draft-rev0253-aiid-not-sent.eml`
- `examples/external-contact-dispatch-authorization-card-rev0253-aiid-blocked-no-signature.json`
- `examples/external-contact-send-branch-handoff-rev0253-aiid.json`
- `docs/30-transition/rev0253-send-branch-operator-handoff.md`

## Queue/refactor audit

The waste corrected here is active-state inflation. In rev0249 the operating board had seven items, but the queue still reported 250 active entries. rev0253 preserves all entries for memory and audit continuity, but defers every non-board active item. The queue now has exactly the seven active board items, and the operating-board report records the deflation.

This does not close first-artifact work by narrative. The live response and evidence tasks remain active until actual dispatch/raw non-host evidence exists or an explicit no-send decision is recorded.

## Current branch

The next non-doctrine action is still a human branch choice:

1. authorize the exact RAIC/AIID send with sender authority, conflict review, private vault root, and transport-proof capture; or
2. record explicit no-send and stop treating silence/no-response as a meaningful state.

## Reliance limits

The shorter draft, public-source contact locator, handoff card, and deflated queue are execution aids only. They do not prove contact, receipt, authority, consent, custody, intake, import, personhood recognition, welfare finding, waiver, adverse inference, or live-floor satisfaction.
