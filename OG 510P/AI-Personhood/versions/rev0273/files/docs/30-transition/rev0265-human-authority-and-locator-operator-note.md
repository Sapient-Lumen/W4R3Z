# rev0265 operator note — exact authority handoff before branch choice

Use this note only if the next branch is a real send or an explicit no-send record. Do not add more doctrine before resolving the branch.

## If the branch is send

Run the existing audits, then complete these human/private steps outside the public release tree:

1. Recheck `https://incidentdatabase.ai/contact/` immediately before dispatch and confirm the collaboration locator is still appropriate.
2. Select the actual sender account/channel and record sender authority.
3. Select private vault roots outside the release tree for sent copy, transport trace, delivery/DSN status, and raw inbound reply.
4. Recompute the body, mail-ready draft, public payload manifest, one-page note, and JSON packet hashes immediately before dispatch.
5. Have the human signer bind the exact recipient, subject, body hash, payload hashes, locator result, sender authority basis, private vault route, and transport-proof capture plan.
6. Send only the public-shell body and the two public payload files if the signer authorizes them.
7. Capture transport proof before reading or classifying any reply.

Do not treat the unsigned precommit, public locator recheck, mail-ready draft, attachment hashes, DSN, auto-ack, sent copy, silence, decline, or any reply as custody, intake, import, waiver, adverse inference, recognition, or live-floor credit.

## If the branch is no-send

Record a no-send decision in the execution record and do not create a no-response shell. A failed-gate summary requires an actual attempted gate or an explicit no-send artifact, not mere elapsed time.

## Legacy replay cleanup

The historical `apply_rev*.py` files are preserved under `tools/legacy-apply-scripts/` with hashes. They are not the current supported replay path. Use `make context-pack`, `make manifest`, `make lint`, and `make package-release` for current release reliance.
