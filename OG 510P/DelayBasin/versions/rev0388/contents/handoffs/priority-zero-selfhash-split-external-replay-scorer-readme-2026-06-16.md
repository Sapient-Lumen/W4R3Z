# Priority-0 selfhash-split external replay scorer kit — 2026-06-16

Open this scorer kit only after the response is frozen and the custody evidence record is complete.

Expected command from the extracted kit root:

```bash
python -S tools/score_priority_zero_external_replay_response.py \
  --scorer-intake assays/priority-zero-selfhash-split-external-replay-scorer-intake-2026-06-16.json \
  --evidence-record <completed-custody-record.json> \
  --score-sheet <completed-score-sheet.json> \
  --summary-out <score-summary.json> \
  <frozen-response.json>
```

The frozen response file must not be edited to add manual scores. Fill `manual_metric_scores` in the separate score sheet after opening this kit. The tool rejects clean strict scoring when manual scores are embedded in the frozen response or when the score sheet does not bind to the custody evidence record.

Self-hash boundary: the responder bundle intentionally does not contain its own expected SHA256. Use the scorer intake and handoff manifest after response freeze to check the responder-observed bundle digest.

Non-claim: a score summary can support the bounded OQ-0265 decision only after clean response, custody evidence, and score sheet all validate. It is not deletion authority, benchmark authority, independent certification by itself, or a review court.
