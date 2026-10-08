# Final-readout redaction refactor — rev0331

## Problem

Rev0330 suppressed exact small cells in the structured `SESSION-LOG.csv` summary, but the result
receipt still copied `FINAL-READOUT.csv` free-text fields verbatim. A local owner could write `2/2`,
`n=2`, `one useful move`, or a percentage in the final readout, and the polished
`MICRO-PILOT-RESULT.json` would carry it even when the session summary correctly masked the same
small cell.

That was a high-risk leak because the final readout is exactly the narrative surface an operator is
most likely to quote, forward, or mistake for evidence.

## Refactor

`tools/record_teacher_tutor_micro_pilot_result.py` now treats `FINAL-READOUT.csv` as an exposure
surface, not a safe mirror:

- Sensitive final-readout rows for baseline, coach use, transfer, move sample, access, and safety are
  scanned for numeric/rate/count/sample language.
- Numeric or small-cell-sensitive final-readout fields are replaced in the receipt with
  `masked_in_result_receipt` language.
- The receipt records `final_readout_suppressed_fields` so a reviewer can see which row/field was
  withheld without seeing the withheld value.
- The bounded row-8 decision remains visible only when it is one of the allowed local decisions.
- Thresholded aggregates should be read from `session_summary`; exact local final-readout text stays
  in the local packet or protected local storage.

## Smoke scenario

A scratch packet with threshold `5`, phase counts of `2`, and final-readout text such as `2/2`,
`n=2`, `50%`, and `one useful move` now records:

```json
{
  "aggregate_value": "masked_in_result_receipt; see thresholded session_summary or local protected packet",
  "method_note": "masked_in_result_receipt; see thresholded session_summary or local protected packet"
}
```

The same result keeps the bounded local decision, workload note, and exact zero stop-trigger counts
where they do not expose a small learner cell.

## Boundary

This is a leak plug and hot-path refactor only. It does not contact an educator, run a cycle, import
evidence, prove learning, support a public claim, authorize service use, or close `FT-0181`.
