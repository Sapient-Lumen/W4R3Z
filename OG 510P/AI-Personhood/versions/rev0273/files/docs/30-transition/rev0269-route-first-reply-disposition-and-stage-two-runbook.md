# rev0269 route-first reply disposition and stage-two runbook

Use this only after the route-first branch is selected by a human operator. It is not a send authorization.

Step 1: before any route-first send, use `examples/external-contact-route-first-send-capture-gate-rev0269-aiid.json`. Do not send unless the human signature, sender authority, send-time locator recheck, private vault roots, final route-first hash recompute, and transport-proof capture plan have been satisfied outside the public release tree.

Step 2: if no message has been sent, keep `examples/external-contact-route-first-reply-disposition-rev0269-aiid-no-inbound.json` in `pre-send-no-inbound`. Do not publish a silence shell, no-response shell, waiver, adverse inference, custody claim, response record, intake record, import gate, status recognition, or live-floor delta.

Step 3: if the route-first message is actually sent, capture the sent copy, provider trace, Message-ID or equivalent, delivery/DSN status when available, final body hash, and private vault locator before reading or classifying any reply.

Step 4: classify inbound material using the route-first reply disposition shell. A DSN or bounce is delivery status only. An auto-ack or ticket is transport trace only. A decline closes the route without adverse inference. A referral requires fresh route-fit review. A redacted-only copy is not raw custody. A protocol/tool output is not authority. A substantive willingness reply is only a candidate for stage-two authorization.

Step 5: use `examples/external-contact-stage-two-authorization-gate-rev0269-aiid.json` before sending the one-page note or machine-checkable packet. Stage two requires fresh human signature, sender authority, locator recheck, private vault roots, payload/body hash recompute, and actual transport proof. A willing route-first reply cannot substitute for those requirements.

Step 6: if stage two is not authorized, preserve the route-first result as a routing outcome only. Keep all downstream gates stayed unless a raw, independently retained, authorized non-host artifact later passes the live evidence path.
