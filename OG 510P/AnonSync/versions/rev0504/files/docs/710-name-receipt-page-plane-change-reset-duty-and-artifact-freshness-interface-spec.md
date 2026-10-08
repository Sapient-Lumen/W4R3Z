# Name receipt page: plane change, reset duty, and artifact freshness interface spec

## Purpose

This receipt proves what the product concluded about a name mutation, which planes changed, what reset or reissue duty remained, and what outward freshness ceiling followed.

## Receipt questions

The receipt must let a later reader answer:

1. what subject and seat were affected
2. what exact name plane changed
3. which planes did not change
4. whether any residue remained or reset was still due
5. whether outward artifacts remained fresh, stale, or required regeneration / reissue
6. what sentence the product was actually allowed to say

## Required fields

- `name_receipt_id`
- `subject_ref`
- `seat_ref`
- `changed_plane`
- `old_value`
- `new_value`
- `unchanged_planes[]`
- `audience_scope`
- `residue_status`
- `reset_required`
- `artifact_freshness_verdict`
- `artifact_followup`
- `strongest_safe_sentence`
- `forbidden_overclaim_sentence`
- `issued_at`

## Presentation order

1. summary strip
2. changed-plane section
3. unchanged-plane section
4. residue / reset section
5. artifact freshness section
6. claim-ceiling section

## Receipt language rules

The receipt must explicitly distinguish:

- `local title changed` from `disk path renamed`
- `artifact label changed for future issuance` from `already-issued artifacts updated`
- `residue still present` from `baseline restored`
- `regenerated current view` from `reissued outward artifact`

## Success criteria

The receipt is successful only when a later operator does not need to reopen tips articles to know what changed, what stayed the same, whether reset was still due, and whether the current outward artifact was still safe to use.
