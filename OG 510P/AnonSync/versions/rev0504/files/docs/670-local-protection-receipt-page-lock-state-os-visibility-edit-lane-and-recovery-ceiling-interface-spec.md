# Local protection receipt page — lock state, OS visibility, edit lane, and recovery ceiling interface spec

## Purpose

This receipt preserves the truth of what happened after a local-protection or external-edit-lane decision.

The operator must be able to answer later:

- what protection state was applied
- what OS visibility changed
- what outside-app edit lane is now in force
- what recovery ceiling was accepted
- what stronger claim remained forbidden

## Receipt sections

The receipt always renders these sections in order:

1. resulting protection state
2. OS visibility verdict
3. external-edit lane verdict
4. recovery ceiling
5. safe sentence / forbidden sentence
6. next review trigger

## Required fields

- `local_protection_receipt_id`
- `seat_ref`
- `subject_scope`
- `resulting_protection_state`
- `os_visibility_verdict`
- `external_edit_lane_verdict`
- `recovery_ceiling`
- `local_only_risk_summary`
- `safe_sentence`
- `forbidden_sentence`
- `next_review_trigger`
- `issued_at`

## Example safe sentences

- `Protection enabled; Files/Recents visibility reduced on this seat.`
- `External editing remains copy-return; modified bytes must be committed back explicitly.`
- `Local recovery ceiling tightened; replicated peers still retain their copies.`

## Forbidden outputs

The receipt must not reduce the outcome to:

- `App locked`
- `Private mode enabled`
- `Edited externally`
- `Recovery available`

Those phrases are too weak to preserve the real contract.

## Non-negotiable rules

### Rule 1 — receipt must preserve the OS delta

If a system surface such as Files/Recents was lost or regained, the receipt must say so.

### Rule 2 — receipt must preserve the edit lane

If the outcome is copy-return rather than live provider editing, the receipt must say so.

### Rule 3 — receipt must preserve the recovery ceiling

If forgetting the local secret could force reinstall or local-only byte loss, the receipt must say so directly.
