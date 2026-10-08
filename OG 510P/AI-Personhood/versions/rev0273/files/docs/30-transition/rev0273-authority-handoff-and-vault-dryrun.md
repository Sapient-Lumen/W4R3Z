# rev0273 authority handoff and vault dry-run operator runbook

Use this only after reading `START_HERE.md` and the dry-run object.

## One-page operator sequence

1. Open `examples/authority-handoff-vault-dry-run-rev0273-reviewer-first-nosend.json`.
2. Decide whether the human branch is no-send, reviewer-first Eleos, two-step route question, AIID route-fit, retarget, defer, or stop.
3. If no-send/defer/stop is selected, record only that branch; do not close the first-artifact duties by narrative.
4. If reviewer-first is selected, create a private signed authority record outside the public release tree and publish only a hash shell using `examples/signed-authority-public-shell-rev0273-template.json`.
5. Select private roots outside the release tree for sent copy, transport proof, raw inbound, legal/conflict notes, and sealed evidence schedule. Do not put raw material in `examples/`, `docs/`, or the ZIP.
6. Recheck the public route and recompute the body, `.eml`, and packet hashes immediately before send. The rev0273 dry-run hashes are not send-time hashes.
7. Send only the exact no-attachment reviewer-first inquiry if the signed branch permits that exact action.
8. Capture raw sent copy and transport/failure proof privately before any public narrative.
9. Classify the first outcome under `examples/reviewer-response-disposition-playbook-rev0273.json`.
10. Publish only an authorized public shell or failed-gate summary; never treat delivery, auto-ack, referral, decline, silence, or a public shell as custody, recognition, or live-floor credit.

## Stop conditions

Stop immediately if the counterparty says do not contact, asks for raw private data, the locator is stale, hashes changed after authorization, private roots are not ready, or the branch authority does not match the contemplated action.
