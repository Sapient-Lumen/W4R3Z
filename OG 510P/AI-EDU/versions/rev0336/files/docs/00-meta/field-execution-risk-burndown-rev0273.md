# Field execution risk burndown rev0273

## Current riskiest failure

After clock bounds, the riskiest internal failure is a returned CSV that bypasses
its own contact provenance. A plausible file path can look more complete than a
real owner relationship. If intake accepts such a file without a source clock,
the cube can make progress inside `scratch/` while the external task remains
unproven.

Rev0273 reduces that risk by binding returned-CSV intake to an active local
contact status.

## Burndown table

| Risk | Before rev0273 | Rev0273 correction | Still not solved |
|---|---|---|---|
| Free-floating returned CSV | Router accepted a plausible local CSV path without checking contact-clock state. | Router blocks returned CSV routing unless the scratch root has an active sent or re-ask contact status. | The archive still cannot prove external delivery or owner identity. |
| Direct intake bypass | `make owner-reply-intake` required only `CSV`. | Make and CLI now require `SOURCE_CONTACT_STATUS` / `--source-contact-status`. | A valid source status is still only local non-evidence. |
| Terminal-state reopening | A CSV could be routed even if local contact state had already reached no-owner-packet. | The source-contact-status integrity check accepts only active sent/re-ask clocks, not terminal no-owner-packet clocks. | A genuinely late owner reply still requires careful new-context handling. |
| Bundle provenance gap | Intake manifest described the CSV but not the contact clock it answered. | Bundle manifest records the source contact-status reference and clock summary. | The manifest still cannot certify truth or accept evidence. |
| Bureaucracy replacing field work | A new doctrine note could have described the problem without changing execution. | The correction is in existing Make targets, router, intake tool, shared guard, and tests. | The external send/adaptation remains the next real action. |

## Refactored surface family

The owner-reply intake family now has a simple provenance chain:

- returned CSVs enter through `owner-field-next`, not direct intake;
- the router selects the latest active contact clock from the scratch root;
- the emitted command includes `SOURCE_CONTACT_STATUS=scratch/.../contact-status.json`;
- intake refuses missing, nonscratch, malformed, terminal, or unbounded contact
  statuses;
- intake records the source-contact-status trace without copying owner answers
  into metadata.

## Completion risk that remains

The most important step is still outside the archive: send or adapt the bounded
packet. The source-clock gate makes the later CSV path harder to fake, but it
does not create the CSV. A clean `NO_OWNER_PACKET` remains better than a local
file that was never tied to the owner-contact attempt.
