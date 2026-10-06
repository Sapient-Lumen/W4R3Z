# Priority-0 preanswer-clamped external replay scorer kit — 2026-06-16

Open this kit only after both the responder-finalized response and completed custody record are frozen.

## 1. Initialize a byte-bound score draft

From the extracted scorer-kit root:

```bash
python -S tools/prepare_priority_zero_external_replay_score_sheet.py init \
  <frozen-response.json> \
  <frozen-custody-record.json> \
  --scorer-id <id-different-from-responder> \
  --out <score-draft.json>
```

The helper reruns the finalized-response contract and the complete shared custody contract before creating a scorer draft. It rejects custody schema drift, false or missing attestations, self-custody, leaked pre-response material, identity/hash disagreement, and malformed local timelines; then it captures scorer-kit initialization time and custody-observation time from its local process clock, binds exact response/custody/scorer-intake bytes, and refuses overwrite.

Fill every numeric metric score, matching metric rationale, and packet-level note. Do not alter response/custody/scorer hashes, contract fields, scorer identity, or helper-captured opening time.

## 2. Finalize the score sheet

```bash
python -S tools/prepare_priority_zero_external_replay_score_sheet.py finalize \
  <frozen-response.json> \
  <frozen-custody-record.json> \
  --draft <filled-score-draft.json> \
  --scorer-id <same-scorer-id> \
  --scorer-notes "manual rubric applied only to the frozen response, custody record, and current scorer kit" \
  --attest-separated-scoring \
  --out <completed-score-sheet.json>
```

Finalization rebinds all exact inputs, rejects responder self-scoring, incomplete metric maps, missing rationales/notes, booleans, non-finite or out-of-range scores, duplicate JSON keys, binding drift, and impossible chronology. It captures `scored_at` automatically and writes a new file without overwrite.

## 3. Run the final scorer

```bash
python -S tools/score_priority_zero_external_replay_response.py \
  --scorer-intake assays/priority-zero-preanswer-clamped-external-replay-scorer-intake-2026-06-16.json \
  --evidence-record <frozen-custody-record.json> \
  --score-sheet <completed-score-sheet.json> \
  --summary-out <score-summary.json> \
  <frozen-response.json>
```

From the full DelayBasin root, the equivalent guarded target is:

```bash
make score-external-response \
  RESPONSE=<frozen-response.json> \
  EVIDENCE=<frozen-custody-record.json> \
  SCORE_SHEET=<completed-score-sheet.json> \
  SUMMARY_OUT=<score-summary.json>
```

The final scorer reruns the same response and custody contracts, binds the exact response → custody → score-sheet hash chain, validates scorer-local opening → custody-observation → scoring order, reconciles packet effort, and refuses global compact-default confirmation from this co-visible trace-excerpt design.

Timestamp boundary: local helper clocks reduce hand-entered defects and are ordered only within the process that emitted them. Cross-operator order is carried by exact artifact hashes, not by comparing independent wall clocks; this is not a trusted timestamp service or independent wall-clock proof.

Non-claim: a score summary is not deletion authority, benchmark authority, measured full-archive marginal-value evidence, independent certification by itself, or a review court.
