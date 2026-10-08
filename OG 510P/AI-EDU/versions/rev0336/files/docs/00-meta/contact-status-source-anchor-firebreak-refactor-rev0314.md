# rev0314 contact-status source-anchor firebreak refactor

## Problem

The contact-status record is the bridge between human owner contact and returned-owner CSV intake. Before rev0314, a valid-looking contact-status JSON could pass later gates without revalidating the source artifact that created it.

The practical failure mode was not fake closure. It was wasted forward motion: a stale or copied contact clock could route a returned CSV into intake/seed/review work even though the actual send/reask source artifact was missing or from the wrong lane.

## Change

`tools/ft0181_field_guards.py` now anchors active contact clocks back to their source artifact when an archive root is available:

- `SENT_AWAITING_REPLY` must point to a field-lane `send-log.json`.
- `REASK_AWAITING_REPLY` must point to a field-lane `reask-log.json`.
- The referenced artifact must exist, be readable JSON, pass its own source integrity guard, and match the contact clock's sent and due dates.

Call sites that source returned CSV intake, workbench seeding, and field routing now pass `archive_root`, so the stronger check runs in the operational path.

## Fixture refactor

`tools/ft0181_validation_fixtures.py` builds positive validator contact clocks through the real packet/send-log/status builders under field-lane validation scratch. This keeps validators realistic without letting checker scratch become a positive provenance source.

## Non-effect

This does not create evidence, send owner messages, accept SRC2+, authorize activation, upgrade public claims, or close `FT-0181`.
