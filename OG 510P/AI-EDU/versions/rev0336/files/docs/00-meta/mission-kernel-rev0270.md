# Mission kernel rev0270

Rev0270 keeps `FT-0181` narrow and operational: get one bounded owner-reviewed
packet for `AIEDU-SR-003`, or fail cleanly without manufacturing local progress.
The change budget is spent on a concrete field-clock weakness: a contact-status
`SOURCE_ARTIFACT` must now resolve to an existing, verified local scratch artifact
of the right type before a sent, re-ask, or no-owner-packet clock can be recorded.

## Current mission

The archive exists to make AI-in-education decisions safer, more contestable, and
more evidence-disciplined. The active field mission is smaller: obtain or boundedly
fail one owner-reviewed packet that can answer whether the draft-reminder service
has a safe action boundary, human fallback, rollback owner, aggregate counts,
workload signal, guidance note, public claim ceiling, and redaction attestation.

## Active kernel path

| Order | Surface | Why it remains first-read |
|---|---|---|
| 1 | `START_HERE.md` | Current executable path and non-evidence boundary. |
| 2 | `AGENTS.md` | Maintainer contract and no-doctrine-sprawl default. |
| 3 | `docs/00-meta/source-artifact-integrity-audit-rev0270.md` | Audit/refactor of the contact-clock source trace. |
| 4 | `docs/00-meta/field-execution-risk-burndown-rev0270.md` | Risk table for false clocks, phantom paths, and wrong-source reuse. |
| 5 | `docs/30-operations/ft0181-owner-request-packet-prep.md` | Packet-prep lane and send-now workflow. |
| 6 | `tools/decide_ft0181_field_next_action.py` | Single next executable command from scratch state. |
| 7 | `tools/prepare_ft0181_owner_request_packet.py` | Builds the outbound packet, brief, memo, and manifest. |
| 8 | `tools/record_ft0181_owner_contact_status.py` | Records local contact state only after confirmation and source-artifact verification. |
| 9 | `docs/30-operations/ft0181-eight-row-owner-reply-sheet.md` | The maximum acceptable owner-reply shape. |
| 10 | `templates/ft0181-eight-row-owner-reply-template.csv` | The only attachment for first contact. |
| 11 | `tools/receipt_owner_reply_csv.py` | Fingerprints a returned CSV without copying answers. |
| 12 | `tools/triage_owner_reply_csv.py` | Blocks protected, overbroad, authority, security, and fixture inputs. |
| 13 | `tools/intake_owner_reply_csv.py` | Writes a local intake bundle after receipt and triage. |
| 14 | `tools/seed_owner_packet_workbench.py` | Creates a NOT_ACCEPTED workbench seed only after PROCEED-STAGED intake. |
| 15 | `docs/30-operations/ft0181-public-outcome-kernel.md` | Keeps public language bounded while the evidence gap remains. |
| 16 | `docs/00-meta/branch-tail-freeze-and-pruning-audit-rev0267.md` | Keeps frozen branch-history surfaces out of the active path. |

## Rev0270 operator firebreak

Rev0269 made contact status require `CONFIRM=` and `SOURCE_ARTIFACT=`. Rev0270
turns that source artifact from a label into an inspected local scratch object.
The recorder now blocks:

- missing or phantom source paths;
- release-controlled files masquerading as source artifacts;
- a `sent-awaiting-reply` clock not sourced from a valid packet manifest;
- a `reask-awaiting-reply` clock not sourced from a due prior sent clock or a
  `RE-ASK-ONCE` intake bundle;
- a `no-owner-packet` clock not sourced from a due prior re-ask clock; and
- packet manifests locally edited to claim evidence, closure, or sent state.

This still does not prove email delivery, owner receipt, or service effectiveness.
It only prevents the local router from advancing on a phantom or wrong-class file.

## What remains blocked

No owner was contacted by this archive. No returned owner CSV exists. No `SRC2+`
evidence has been imported. No live-window readout, custody workbench acceptance,
closure minutes, or public claim upgrade exists. The next meaningful field step is
still external human contact or a returned-owner intake; rev0270 only makes the
local clock harder to fake.
