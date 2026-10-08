# rev0257 route-first no-attachment operator note

Use this note only if the next operator is considering first external contact.

## Preferred first hop

Prefer `examples/external-contact-route-first-mail-ready-draft-rev0257-aiid-not-sent.eml` over the attachment-bearing full-payload draft for the first hop. It asks a routing/willingness question and includes no attachments. This reduces three practical risks: mail filtering, counterparty overload, and misclassification as an AIID incident submission.

## Before any route-first send

The operator still needs:

1. signed human authorization over the exact route-first subject, recipient, body hash, sender role, no-attachment limit, and stage-two deferral;
2. sender authority for the account/channel used;
3. send-time public locator recheck;
4. private vault roots for sent copy, transport trace, delivery or DSN status, and any raw reply;
5. final route-first body and `.eml` hash recompute;
6. transport-proof capture before any response or no-response clock starts.

## Stage two

The public payload manifest remains available, but it should travel only after counterparty willingness or separate human authorization. A request for “send more detail” is still not custody, intake, import, recognition, or live-floor evidence; it only permits the operator to consider a second authorized send.

## Failure handling

If there is no authorization, record no-send. If the route-first message is later actually sent and there is silence, do not prepare a failed-gate shell until transport proof exists and the actual sent timestamp determines the response window. Auto-acks, DSNs, referrals, and declines must continue through response triage.
