# rev0293 field-execution risk burn-down

| Rank | Risk | rev0293 response |
|---|---|---|
| 1 | A real human sends/adapts the packet, but local send-log and contact-clock recording is split across multiple commands and gets missed. | Added `make owner-after-human-send`, which requires the human-send confirmation token and records both `send-log.json` and a sourced `SENT_AWAITING_REPLY` contact clock. |
| 2 | Operators keep reading packet docs instead of making the first field move. | Front-door docs now name the compact path: `owner-field-work` before send, router-emitted `owner-after-human-send` after actual send, and route-block if no accountable route exists. |
| 3 | The helper could be mistaken for proof of delivery or owner evidence. | The helper stores no recipient details or owner answers and writes `AFTER-HUMAN-SEND-SESSION.md` as `not_evidence`, `does_not_close_ft0181`, and `public_claim_effect=none`. |
| 4 | Existing send-log/contact-status repair paths drift from the preferred path. | The router still validates already-written send logs and can emit lower-level contact-status repair commands; the new helper reuses the same builders and source-artifact checks. |
| 5 | Fixing the first-contact rail weakens post-readout context receipt controls. | No post-readout intake shortcut was added; context receipt remains provenance/reroute only and must be paired with the same actual CSV/source packet. |

## Remaining live blocker

No real owner has been contacted in this release archive, no real CSV has been
received, no accepted `SRC2+` packet exists, no real live window has run, no
owner-held post-readout action has occurred, and no real post-readout context
receipt/intake cycle has occurred. `FT-0181` remains live.

## Correct next move

Use the compressed local field-work target:

```bash
make owner-field-work OUT=scratch/ft0181-field-work/aiedu-sr-003
```

After a human actually sends/adapts the packet, run the router and execute only
the emitted `owner-after-human-send` command. Do not run it before the send. If
no accountable owner route exists, use the emitted `owner-route-block` fallback
instead of inventing a recipient, recording a fake send log, or adding another
control surface.
