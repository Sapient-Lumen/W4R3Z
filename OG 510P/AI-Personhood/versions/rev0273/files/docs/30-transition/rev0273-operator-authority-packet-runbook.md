# rev0273 operator authority packet runbook

Use this runbook only after reading `examples/operator-authority-packet-compiler-rev0273-reviewer-first-no-signature.json`.

The current state is no-send. The compiler is public and hash-bound, but it is not authority. It is a checklist of what remains missing before any real action.

## Current decision

Choose exactly one private branch:

1. `NO-SEND`
2. `DEFER`
3. `STOP`
4. `ONE-SHOT-REVIEWER-FIRST-SEND`

No branch exists until a private operator identity and signature record exists outside the public release tree.

## Before any one-shot send

Abort unless all of the following are true:

- The private operator identity and role are recorded.
- The branch value is signed and unexpired.
- Private roots are selected outside the public release tree for raw sent copy, transport proof, raw inbound, classification notes, sealed evidence, and signature record.
- The Eleos route locator is rechecked immediately before send.
- The exact recipient, subject, sender, body, `.eml`, no-attachment scope, and one-shot limit match the signed branch.
- The message body and `.eml` hashes are recomputed at send time.
- Transport proof or failed-send proof can be captured privately before any public summary.
- Response handling will use the response-disposition playbook before any public narration.

## Abort conditions

Abort as `NO-SEND-FAIL-CLOSED` if any of these occur:

- Signature missing or expired.
- Private roots missing.
- Public route facts changed or expired.
- Recipient, subject, sender, body, `.eml`, attachment scope, or one-shot limit differs from the signed branch.
- Transport capture cannot be preserved.
- The counterparty indicates do-not-contact or no fit.
- The only signal is delivery metadata, an auto-ack, silence, or a web-form receipt.

## What may be published

Without private authorization, publish only public no-send/fail-closed state. With a failed send, publish only a failed-gate summary after private failed-send proof is captured. With a human decline, referral, narrow yes, or private-data request, publish only the response-disposition class and permitted hash-only shell.

Do not publish raw private paths, raw signatures, raw headers, raw inbound material, sealed evidence, or identity material in the public cube.

## What still cannot be claimed

The compiler does not prove contact, delivery, response, custody, intake, import, reviewer appointment, preservation agreement, welfare finding, recognition, or live-floor effect.
