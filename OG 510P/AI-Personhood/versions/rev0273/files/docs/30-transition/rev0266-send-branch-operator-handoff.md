# rev0266 send-branch operator handoff

This is the smallest next action surface. It is not a send, transport proof, delivery status, response, custody, intake, import, recognition, waiver, adverse inference, or live-floor event.

## Branch A — send only if all cells are filled

Use `examples/external-contact-send-branch-handoff-rev0266-aiid.json` together with `examples/external-contact-public-payload-manifest-rev0266-aiid.json` and `docs/30-transition/rev0266-exact-payload-operator-checklist.md`. Sending requires a human signature, sender-authority attestation, conflict-review acceptance, an off-release private vault root, a transport-proof capture plan, and exact body/public-payload hash verification. The exact outgoing body hash is `d6c55f018d7277b3069629ddf3ab22c19f244989b9424ae1ded4c96054030c6e`.

The public locator is `info@raicollab.org`, recorded only from the AIID contact page as a collaboration channel. The locator is not consent or authority.

## Branch B — no-send

If any required cell is missing, record no-send. Do not manufacture a no-response, failed-gate, custody, intake, import, waiver, adverse-inference, status, or live-floor shell against a counterparty that was not contacted.

## After any real send

Only after actual dispatch, update the send-proof record and send-trace shell from private raw transport evidence. Auto-acknowledgement, DSN, delivery status, provider UI, Message-ID, silence, decline, or a human reply must enter response triage before any downstream evidence step.
