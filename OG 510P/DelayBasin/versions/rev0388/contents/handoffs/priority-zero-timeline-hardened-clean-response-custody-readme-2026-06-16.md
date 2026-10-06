# Priority-0 clean-response custody record README — 2026-06-16

Create the custody evidence record only after the response is frozen and before scorer intake is opened.

Required custody constraints:

- `custodian_id` must be non-empty and must differ from the response `responder_id`.
- `responder_id` must match the frozen response `responder_stage.responder_id`.
- All chronology timestamps must include timezone offsets.
- Timestamp order must be `run_started_at <= run_completed_at <= response_frozen_at <= scorer_opened_at`.
- Pre-response material must be limited to `handoffs/priority-zero-timeline-hardened-external-replay-responder-bundle-2026-06-16.zip`.
- The record is evidence of custody posture only; it does not prove semantic correctness or external replay success.

Use `tools/prepare_priority_zero_clean_response_custody_record.py` after response freeze to reduce clerical hash errors, then score with `tools/score_priority_zero_external_replay_response.py --evidence-record <record> <response>`.
