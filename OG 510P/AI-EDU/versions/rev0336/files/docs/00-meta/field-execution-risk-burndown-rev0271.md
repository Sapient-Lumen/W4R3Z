# Field execution risk burndown rev0271

## Current riskiest failure

The riskiest remaining failure is not missing doctrine. It is a local operator
advancing the field clock without an external send actually happening, then later
mistaking that clock for owner evidence.

Rev0271 reduces that risk by splitting the first contact into two local artifacts:
`send-log.json` and `contact-status.json`. The split matters because the first is
an operator assertion about a human action, while the second is only the response
clock state created from that assertion.

## Burndown table

| Risk | Before rev0271 | Rev0271 correction | Still not solved |
|---|---|---|---|
| Prepared packet masquerades as sent | Packet manifest could source `SENT_AWAITING_REPLY`. | Sent status must source `send-log.json`. | Delivery and receipt remain external. |
| Copied router command creates false clock | Operator could run contact-status command after packet prep. | Router first emits `make owner-send-log`; contact recorder blocks packet source. | A dishonest operator can still lie locally. |
| Contact details leak into release | Send/adaptation notes could tempt address or header capture. | Send log stores only channel class and owner-route class. | External mail/ticket system remains outside archive. |
| Stale local files confuse re-entry | Old status or note could survive repeated runs. | Packet, send-log, and contact targets clear stale files with `OVERWRITE=1`. | Operators must still use scratch or external local paths. |
| More registry work displaces field work | Each gap could create a new prose surface. | Change is concentrated in Makefile, router, send-log tool, contact verifier, and tests. | Real owner contact still has to happen outside this archive. |

## Refactored surface family

The first-contact family now has a stricter sequence:

- packet prep: `PREPARED_NOT_SENT`;
- send log: `LOCAL_SEND_LOG_NOT_EVIDENCE`;
- contact status: `SENT_AWAITING_REPLY`, `REASK_AWAITING_REPLY`, or
  `NO_OWNER_PACKET`;
- returned CSV intake: only for plausible non-fixture owner CSV paths;
- workbench seed: `NOT_ACCEPTED` until manual review.

This refactor removes the direct packet-to-sent shortcut and avoids adding a new
policy registry. The field lane now burns down an actual operational seam.

## Completion risk that remains

The owner may still be unavailable, the route may be wrong, or the owner may
refuse to answer safely. That is acceptable. A bounded `NO_OWNER_PACKET` after
one clarification is a better field result than a wider data request, copied
owner prose, synthetic evidence, or another long control branch.
