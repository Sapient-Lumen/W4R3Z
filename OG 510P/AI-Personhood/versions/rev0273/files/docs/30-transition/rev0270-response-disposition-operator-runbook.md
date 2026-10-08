# rev0270 response disposition operator runbook

This runbook prevents the first real-world ambiguity from being laundered into progress.

## Decision ladder

- No human authority: keep A1 prepared-not-authorized; do not send.
- Send failed: record A2 failure proof privately; public shell may state failed send only.
- Delivery-only: classify as transport metadata, not response.
- Auto-ack or bot reply: classify as status unless later human-confirmed.
- Human decline or do-not-contact: publish only a non-waiver failed-gate shell; respect the boundary.
- Referral or wrong route: create a retarget branch decision; do not treat referral as appointment.
- Narrow yes to scoping: open only reviewer-scoping; do not claim reviewer appointment, welfare finding, or custody.
- No response after expiry: publish expired-no-response shell; do not infer status or waiver.
- Raw private data requested: stop public handling and route to private custody/legal review.

## Required public shell

Use `examples/failed-gate-public-summary-rev0270-reviewer-route-unavailable-template.json` whenever A3 or A6 fails. It must say that failed-gate publication does not satisfy live receipt, recognition, waiver, or review.
