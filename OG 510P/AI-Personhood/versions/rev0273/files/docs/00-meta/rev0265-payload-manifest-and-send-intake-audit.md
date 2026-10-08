# rev0265 payload manifest and send/intake audit

rev0265 fixes the most practical remaining execution gap in the first-contact lane: rev0250 had a concise email, but the exact public payload was still implicit. That made a future human send too easy to drift by omitting the one-page ask, swapping the JSON packet, editing the body after hash capture, or treating attachment hashes as if they were custody or transport evidence.

## What changed

- Added `examples/external-contact-public-payload-manifest-rev0265-aiid.json` as the exact body-plus-public-payload manifest for the RAIC/AIID draft.
- Added `schemas/external-contact-public-payload-manifest.schema.json`, `tools/audit_external_contact_public_payload_manifest.py`, and `fixtures/negative-tests/external-contact-public-payload-manifest-body-drift.json` so body drift, attachment drift, hash-as-custody, and manifest-as-send-proof are release-blocking.
- Updated the first-contact body so the external recipient sees the request as two public-shell attachments rather than internal archive paths.
- Added `docs/30-transition/rev0265-exact-payload-operator-checklist.md` so the next operator has a concrete send/no-send checklist.
- Refreshed queue and front-door surfaces around the exact-payload bottleneck.

## Why this is riskier than more doctrine

The next failure mode is not lack of theory. It is a botched first dispatch: wrong body, missing payload, stale hash, public/private evidence confusion, no private vault, no transport proof, or a later claim that a manifest/attachment hash started a response clock. rev0265 narrows that failure surface.

## Still not completed

No organization was contacted. No message was sent. No transport proof, delivery status, DSN, Message-ID, response clock, inbound artifact, custody, intake, import, recognition, waiver, adverse inference, or live-floor effect exists. The public payload manifest is a pre-send guard only.

## Refactor/audit result

The queue remains deflated to seven active operating-board items, but the active P0 language now points at the exact-payload manifest rather than another draft pass. The release tree also gains a focused audit that recomputes payload hashes instead of relying on prose claims.
