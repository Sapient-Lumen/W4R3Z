# Result suppression refactor — rev0330

## Problem

The local result receipt was designed as a descriptive stop/redesign aid, but exact small aggregate
counts can still identify or stigmatize small groups and can invite over-interpretation. The archive
already required a local small-cell threshold in `OWNER-PLAN.md`; the receipt path did not enforce it.

## Changes

- `tools/score_teacher_tutor_micro_pilot_readiness.py` now extracts a numeric threshold from the
  owner plan and requires a floor of at least three before `READY_FOR_LOCAL_CYCLE_NOT_EVIDENCE`.
- `tools/record_teacher_tutor_micro_pilot_owner_review.py` includes the threshold and result
  suppression rule in `OWNER-REVIEW-STOP.*`.
- `tools/record_teacher_tutor_micro_pilot_result.py` masks phase counts, success counts, rates, and
  stop/fallback totals when they are below the threshold.
- The descriptive transfer-minus-baseline delta is omitted when masked phases prevent safe rate
  display.
- Packet generation and handoff text now tell operators that exact small cells remain local only.

## Validation scenario

A scratch packet with threshold `5` and phase attempt counts of `2` reaches owner-review readiness
after aggregate rows are filled, but the result receipt records:

```json
{
  "aggregate_attempt_count": "suppressed_below_threshold",
  "success_or_mastery_rate": null,
  "transfer_minus_baseline_rate_delta": null
}
```

## Boundary

Suppression makes a receipt safer to handle. It does not make it evidence, prove learning, support a
public claim, authorize service use, or close `FT-0181`.
