# rev0271 authority expiry and pre-send evidence refactor

## Why this exists

rev0268 made the reviewer-first branch executable as a dry run, but it still left one practical danger: readiness can go stale. A route page can change, the chosen sender can lose authority, the message bytes can drift, or the operator can forget where raw transport and inbound records will be captured.

rev0271 therefore adds an expiry layer. A prepared packet remains below authority unless all of the following are true at the same time: a private signed branch exists, the public authority shell reflects only that private record by hash, private vault roots are selected outside the release tree, the route locator has been freshly rechecked, packet/body/.eml hashes are recomputed at send time, and a one-shot evidence bundle binds the response-disposition playbook before contact.

## Operational change

The new surfaces are intentionally action-facing:

- `examples/route-locator-freshness-ledger-rev0271-public-source-no-contact.json` records current public-source route facts and an expiry window. It is evidence of public observation, not consent or authority.
- `examples/authority-expiry-and-renewal-check-rev0271-no-signature.json` records how a future private branch decision expires and must be renewed. No signature exists now.
- `examples/pre-send-evidence-bundle-rev0271-reviewer-first-no-send.json` binds the route ledger, authority expiry check, handoff dry run, reviewer-first packet, body, `.eml`, and response playbook into one no-send dossier.
- `tools/audit_rev0271_presend_expiry.py` rejects stale route facts, stale hashes, missing source bindings, public private-root leakage, send-window overclaiming, and queue closure by stale readiness.

## Anti-bureaucracy rule

This refactor must not become another registry layer. It exists to remove excuses at the human-action boundary. If no human signs, the next truthful state is no-send/defer/stop, not another doctrinal object. If a human does sign later, this release still cannot be used directly; the route locator and hashes must be recomputed at send time and private roots must be recorded outside the public tree.

## Reliance limits

The new bundle is not a send, not a delivery record, not raw custody, not an inbound artifact, not reviewer appointment, not welfare finding, and not live-floor evidence. It is a fail-closed bridge from preparation to the first external artifact attempt.
