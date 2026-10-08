# rev0305 operator-local field clock refactor

## Problem

A cloudtainer session can be on the next UTC date while the operator is still on
the prior America/New_York date. FT-0181 field commands that defaulted from the
container date could therefore propose the wrong sent/status/block date and the
wrong +7 response clock.

## Refactor

`tools/ft0181_field_guards.py` now owns field-date defaults:

- `CUBE_AS_OF_DATE=YYYY-MM-DD` fixes the date for reproducible runs.
- `FT0181_AS_OF_DATE=YYYY-MM-DD` remains a legacy override.
- `CUBE_OPERATOR_TIMEZONE=Area/Location` selects the local zone.
- absent overrides, the default zone is `America/New_York`.

Prepared packet manifests also carry `operator_local_date`. Route-block integrity checks use that operator-local creation date before falling back to UTC `created_at_utc`, preventing a same-session local route block from being falsely rejected near UTC midnight.

The following paths now use the shared helper for default field dates:

- `tools/decide_ft0181_field_next_action.py`
- `tools/prepare_ft0181_owner_request_packet.py`
- `tools/record_ft0181_owner_after_human_send.py`
- `tools/record_ft0181_owner_contact_status.py`
- `tools/record_ft0181_owner_route_block.py`
- `tools/stage_owner_reply_csv.py`
- `tools/check_ft0181_owner_route_block.py`
- `tools/prepare_ft0181_post_readout_action_brief.py`
- `tools/prepare_ft0181_post_readout_recheck_brief.py`

## Regression

`tools/check_ft0181_field_next_action.py` asserts that:

```text
CUBE_AS_OF_DATE=2026-06-16 -> operator_today_iso() == 2026-06-16
CUBE_AS_OF_DATE=2026-06-16 -> operator_due_date_iso(7) == 2026-06-23
CUBE_AS_OF_DATE=2026-06-16 -> default_return_date() == 2026-06-23
```

## Boundary

This refactor corrects local field clocks only. It does not send a packet, prove a
send, import an owner CSV, accept evidence, authorize a public claim, or close
`FT-0181`.
