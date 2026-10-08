# Teacher/tutor feasibility result recorder

This recorder summarizes a completed, human-reviewed local packet after `OWNER-REVIEW-STOP.json`
exists and the packet hashes still match. It is a descriptive local receipt, not an evidence intake.

## Command

```bash
make micro-pilot-result \
  PACKET=scratch/field-handoff/rev0336/teacher-tutor-micro-pilot/teacher-selected-concept \
  OWNER_REVIEW=scratch/field-handoff/rev0336/teacher-tutor-micro-pilot/teacher-selected-concept/OWNER-REVIEW-STOP.json \
  RECORD_DATE=YYYY-MM-DD \
  OPERATOR_ROLE="local feasibility operator role only" \
  CONFIRM=human-recorded-local-micro-pilot-aggregate-result \
  OVERWRITE=1
```

The recorder checks readiness, rejects dry runs, verifies the review record and packet hashes, verifies event chronology,
requires the final decision to match, summarizes aggregate phase counts and minutes, and masks exact
counts/rates below the owner-plan small-cell threshold. It calculates a descriptive
transfer-minus-baseline difference only when baseline and transfer rates are safe to display. That
arithmetic is not a causal estimate.

## Final-readout redaction

`FINAL-READOUT.csv` is a local owner-review surface, not a safe export surface. Rev0331 redacts
numeric or small-cell-sensitive final-readout free text in the result receipt and records only the
row/field coordinates in `final_readout_suppressed_fields`. Use `session_summary` for thresholded
aggregates; exact final-readout small-cell text remains local or protected outside the archive.

A result receipt now includes `decision_followthrough`. Exact small-cell values must remain local and outside the receipt. The follow-through map means: `retire` stops; `repeat-narrower` and `continue-bounded` require a fresh packet and cannot pool cycles as evidence; `escalate-to-pilot-review` requires a separate future gate. It must not update service authority, enter a public claim, or be treated as `SRC2+` merely because it is well structured.

## Boundary

The receipt does not prove learning, access, safety, fairness, workload reduction, effectiveness,
compliance, deployment readiness, custody, or `FT-0181` closure.

## rev0336 provenance check

Before recording a local result, the recorder compares the current packet hashes to the
`OWNER-REVIEW-STOP.json` hash scope. That scope now includes the coach prompt, checklist, measure card,
discovery card, and cycle run sheet. A result receipt must not summarize a packet whose run-defining
instructions changed after owner review.

## rev0336 event chronology check

Before writing `MICRO-PILOT-RESULT.*`, the recorder rechecks `SESSION-LOG.csv` chronology, verifies the owner-review date is on or after the latest session date, and verifies the result record date is on or after both the owner-review date and latest session date. A receipt must not summarize an impossible sequence.

## rev0336 decision follow-through check (prior)

`MICRO-PILOT-RESULT.json` carries `decision_followthrough` so the completed artifact has one bounded next action instead of a vague stop. The next-action router reads that map when the result exists. No decision opens evidence custody, service authority, public-claim support, or `FT-0181` closure.

## rev0336 follow-through seed receipt boundary

`MICRO-PILOT-RESULT.json` now records `decision_followthrough_spec` and `fresh_packet_preflight`. These fields confirm that a post-result seed was checked before review, but they do not copy the seed text. A fresh packet after `repeat-narrower` or `continue-bounded` must be filled from local owner choices; cycles must not be pooled as evidence.

## rev0336 fresh-packet source rule

For `repeat-narrower` and `continue-bounded`, the result receipt is the source for exactly one fresh local packet. The follow-through packet must be generated with `SOURCE_RESULT` and the confirmation token, which records a hash link but does not import the result as evidence or copy owner seed text into the new packet.
