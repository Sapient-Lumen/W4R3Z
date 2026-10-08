# rev0268 route-first reply disposition and stage-two gate refactor

rev0268 is an execution-risk pass. It does not add doctrine, does not send anything, and does not move the live floor. It closes the next practical gap after rev0257: the no-attachment route-first branch had a send/capture/reply ladder, but it did not yet have a route-first-specific no-inbound disposition shell or a separate gate preventing a willing reply from becoming an automatic stage-two payload send.

The riskiest unresolved point is no longer drafting. The risk is operator drift after a route-first send: a bounce, auto-ack, referral, willing note, redacted copy, or protocol/tool output could be mistaken for custody, intake, import, authority, or permission to transmit the preservation/formation packet. rev0268 adds two bounded controls:

- `examples/external-contact-route-first-reply-disposition-rev0268-aiid-no-inbound.json` classifies future route-first inbound material while keeping the current state no-inbound.
- `examples/external-contact-stage-two-authorization-gate-rev0268-aiid.json` blocks the two-file stage-two payload until there is fresh authorization, hash recompute, private vault routing, and transport proof.

The older full-payload response triage remains useful historical context, but it is no longer the active first branch. The active branch is now: route-first no-attachment draft → route-first send/capture gate → route-first reply disposition shell → blocked stage-two authorization gate. The packet stays deferred.

The new failure modes blocked are concrete:

- treating a willingness reply as permission to send attachments automatically;
- treating an auto-ack, DSN, referral, or redacted-only reply as a human substantive response;
- treating a route-first reply as custody, intake, import, status recognition, or live-floor evidence;
- treating the public payload manifest as transport proof or authorization;
- letting the old full-payload triage path become the de facto front door again.

The state remains stayed: no send, no contact, no transport proof, no delivery status, no DSN, no Message-ID, no response clock, no inbound artifact, no custody, no intake, no import, no recognition, and zero live floor. The next real action is still a human branch decision: send the route-first no-attachment inquiry with proof, or record an explicit no-send reason.
