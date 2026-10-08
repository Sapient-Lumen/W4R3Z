# rev0269 pre-send expiry and evidence runbook

## Operator sequence

1. Read `examples/pre-send-evidence-bundle-rev0269-reviewer-first-no-send.json`.
2. Choose one branch: no-send, defer, stop, reviewer-first Eleos inquiry, AIID route-fit inquiry, two-step route question, or retarget.
3. If the branch is no-send/defer/stop, record that privately and leave all A1-A6 live-artifact lanes open or explicitly failed; do not narrate closure.
4. If the branch is reviewer-first, create a private signed authority record outside the release tree, then publish only a hash shell if public disclosure is authorized.
5. Select private roots outside the release tree for sent copy, transport proof, delivery/DSN/bounce, raw inbound, legal/conflict notes, and sealed evidence schedule.
6. Recheck the public route locator and recipient immediately before send. If the route ledger has expired, renew it before doing anything else.
7. Recompute body, `.eml`, packet, and public-shell hashes immediately before send. The dry-run hashes in this release do not satisfy that send-time duty.
8. Send only the hash-bound no-attachment reviewer-first inquiry if all gates are green.
9. Classify the first outcome through `examples/reviewer-response-disposition-playbook-rev0269.json` before any public summary.

## Fail-closed outcomes

- No signature: no-send/no-authority.
- Signature but expired route facts: renew route ledger or stop.
- Signature but missing private roots: no-send.
- Signature and roots but hash drift: no-send until recomputed and rebound.
- Delivery-only or auto-ack: transport status only.
- Decline, referral, silence, or out-of-scope answer: failed-gate shell only, no adverse inference.
- Narrow willingness: candidate only; still no custody/intake/import/floor until later gates.

## What not to do

Do not send attachments in the route-first branch. Do not treat public contact information as consent. Do not store raw private mail, headers, DSNs, signatures, or correspondence in the release ZIP. Do not let a green audit become a substitute for human branch authority.
