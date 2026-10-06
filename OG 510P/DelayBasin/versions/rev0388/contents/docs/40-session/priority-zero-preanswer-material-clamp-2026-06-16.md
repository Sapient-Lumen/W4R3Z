# Priority-0 pre-answer material clamp and score-time guard — 2026-06-16

## Concrete defect

`rev0373` repaired the responder-bundle self-reference, but the clean-response admission path still had one serious leak-shaped weakness: a custody record could name the responder bundle while also admitting that an old submission kit, custody kit, score sheet, handoff manifest, expected digest material, scorer kit, or prior conversation was shown before the responder froze an answer. The scorer only required the responder bundle to be present in `pre_response_materials_given`; it did not require the pre-answer material list to be exact.

That is not a doctrine problem. It is a runnable-evidence blocker. A response produced after seeing a submission/custody/scorer packet could look custody-clean while carrying post-freeze cues. The cube would then be vulnerable to accepting contaminated evidence as clean external replay.

## Repair

`rev0374` makes the pre-answer material exact-match boundary explicit. A clean admissible run must show exactly one pre-answer material surface:

`handoffs/priority-zero-preanswer-clamped-external-replay-responder-bundle-2026-06-16.zip`

The custody kit and scorer kit are post-freeze material only. The post-freeze custody kit exists so a distinct custodian can bind the frozen response hash, responder bundle hash, responder packet hash, response template hash, and chronology after the responder has completed the answer. The scorer kit exists only after the custody evidence record is complete.

## Score-time chronology guard

This section is the score-time chronology guard.

The score sheet now has its own chronology guard. In strict clean scoring, `scorer_attestation.scored_at` must be timezone-bearing and must not precede either `response_frozen_at` or `scorer_opened_at`. This closes the remaining gap where a separate score sheet could be hash-correct but time-impossible.

## Negative canaries

The current checker rejects these cases:

- a custody record that includes any material besides the responder bundle before response;
- an old submission kit, custody kit, scorer kit, score-sheet material, manifest, expected digest, full archive, receipt, resolution ledger, or prior conversation shown before response;
- a score sheet whose `scored_at` is before response freeze or before scorer open;
- a missing clean response being treated as compact-gate confirmation.

## Non-claim

This revision does not collect a clean external/operator-independent response. It does not confirm compact reentry, authorize deletion, certify a benchmark, or act as a review court. It only repairs the admission boundary so the next response/custody/score-sheet triplet can be evaluated without pre-answer leakage or score-time impossibility.

## Live successor

`OQ-0266` is live: collect a clean external/operator-independent response using only the preanswer-clamped responder bundle, freeze it, then open the post-freeze custody kit to create a chronology-valid distinct-custodian custody evidence record, and finally open the scorer kit to fill the separate score sheet and run the scorer.

## Working-overlay execution correction — three-stage chronology

A later executable audit found that the earlier prose required the custody record to freeze before scorer material opened while the custody template simultaneously required `scorer_opened_at`. That forced an operator either to open scorer material too early or to forecast a future timestamp in a supposedly frozen record.

The working-overlay repair separates the stages truthfully:

`response complete <= response frozen <= custody kit opened <= custody record frozen <= scorer kit opened <= score sheet scored`

The custody record now ends at `custody_record_frozen_at`. The score sheet records `scorer_kit_opened_at` and `scored_at`. The current custody and score-sheet helpers bind exact bytes and fail closed on stage inversion. Historical scorer fixtures retain their legacy chronology only for replay compatibility.
