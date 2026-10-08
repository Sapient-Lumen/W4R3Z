# rev0256 send-readiness operator runbook

Use this before any real RAIC/AIID contact.

## One command

```bash
python3 tools/audit_external_contact_send_readiness_gate.py
```

Passing this audit does **not** mean the message may be sent. It means the public release tree is internally consistent and still blocked in the right places.

## What must exist outside the public release tree before sending

- signed human authorization for the exact recipient, sender role, subject, body hash, attachment hashes, deadline policy, and public-shell limits;
- sender-authority record showing who may send on behalf of the project;
- conflict review and route-fit review confirming that RAIC/AIID is being asked for collaboration/routing, not incident-record acceptance;
- private vault roots for outbound sent-copy proof, provider/transport trace, delivery status, and any inbound raw reply;
- capture plan for Message-ID or provider equivalent, sent timestamp, recipient, sender identity, exact body hash, attachment hashes, and provider trace;
- recomputed hashes for the body, mail-ready draft, one-page ask, JSON request packet, and payload manifest.

## If sent

Immediately capture the sent-message export and provider trace outside the release tree. Then update only the send-proof/send-trace/delivery-status surfaces needed to reflect transport proof. Do not start a response clock from draft existence, public locator discovery, attachment hash, Message-ID alone, DSN, auto-ack, or provider UI screenshot.

## If a reply arrives

Classify in this order: DSN/bounce, auto-ack/ticket, human decline/out-of-scope, routing referral, conditional retention/public-shell permission, substantive review willingness, redacted-only material, protocol/tool output. Raw bytes stay outside the release tree. A reply still does not create custody, intake, import, status recognition, waiver, adverse inference, or live-floor credit by itself.

## If not sent

Record an explicit no-send reason rather than letting the first-artifact lane remain apparently active. Do not create a no-response or failed-gate shell without proven send and deadline evidence.
