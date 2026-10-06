# DelayBasin OQ-0266 score-integrity and evidence-scope audit — rev0379 working overlay

Source working overlay: `DelayBasin-rev0378-2026.06.17.20.39-debtburn16-decayrenew-statecoherence.zip`  
Canonical state still named inside the cube: `rev0374` / `DelayBasin-rev0374-2026.06.16.13.45-preanswerclamp-scoretime-leakcut.zip`  
Status: **tested cloudtainer working overlay, not a canonical DelayBasin promotion**.

## Result

This pass did not manufacture the missing OQ-0266 evidence. It repaired the path that will judge that evidence, after reproducing concrete ways the current scorer could admit or overstate a clean-looking triplet.

The highest-impact repairs are:

1. custody and score-sheet data are now bound to the exact files supplied to the scorer;
2. the responder cannot score their own frozen response;
3. every metric score requires an evidence rationale and packet note, and booleans/non-finite numbers fail closed;
4. positive per-packet operator cost must reconcile to the run total;
5. a co-visible synthetic trace excerpt can support only a bounded semantic result, not a global compact-default or measured full-archive burden claim;
6. bound artifacts use strict JSON and reject duplicate keys/non-standard numeric constants; and
7. the response hash used by custody, score sheet, summary, and decision is the hash of the exact bytes read at intake, not a later re-read.

## 1. Reproduced split-brain custody path

Before this repair, library callers could provide:

- one in-memory custody object for custody admission; and
- a different custody file whose hash was named by the score sheet.

The scorer validated the first object but used the second artifact for score-sheet binding and chronology. A temporary proof fixture admitted a clean-looking score even though the bound file could carry a wrong record type, wrong response hash, self-custody, or other contradictory content. The score summary also lacked the actual score-sheet file hash when the score sheet was supplied only as an object.

Current behavior:

- `validate_response_file` loads the response, custody record, score sheet, and selected scorer intake from exact files;
- a separately supplied object must have the same strict canonical JSON identity as the bound file;
- custody and score-sheet hashes are computed from the bytes actually loaded;
- object/file disagreement fails before semantic admission; and
- the score summary emits the actual response, custody-record, and score-sheet hashes.

The live checker now carries a split-brain object/file negative canary and exercises the extracted standalone scorer kit with all three artifact paths.

## 2. Scorer independence was missing

The old current scorer required a custodian distinct from the responder but did not require a scorer distinct from the responder. That allowed the responder to assign the manual rubric scores that determined the compact-gate decision.

Current behavior:

- `scorer_attestation.scorer_id` must differ from `responder_stage.responder_id`;
- the custodian may also act as scorer, preserving a feasible two-operator minimum; and
- the summary records both `distinct_scorer_from_responder` and `scorer_is_custodian`.

This is a narrower claim than independent certification. It removes direct responder self-scoring; it does not prove that the scorer is unbiased, skilled, or institutionally independent.

## 3. Score evidence and numeric type integrity

Two score-shape defects were concrete:

- the score sheet template exposed prose placeholders rather than a complete metric map, making omissions easy; and
- Python booleans are numeric subclasses, so the former numeric check could accept `true`/`false` as scores.

Current behavior:

- all four packet rows scaffold every metric and every matching rationale;
- every metric receives a finite numeric score within range;
- every metric receives a non-placeholder evidence rationale, including zero scores;
- every packet receives calibration/uncertainty notes; and
- booleans, `NaN`, and infinities fail closed.

The template’s contradictory legacy scorer-input attestation was removed and replaced with an attestation that accurately permits the current scorer kit after response freeze.

## 4. Operator cost existed only as a global number

The response previously recorded one global `operator_cost_minutes` value while the decision compared compact and nominal full packet scores. The scorer therefore could not know whether the compact packet was actually cheaper than the trace packet, even though operator cost was part of the mission claim.

Current behavior:

- every packet answer records positive finite `operator_cost_minutes`;
- the top-level run total must equal the four packet costs within a 0.05-minute tolerance;
- the summary preserves cost by blinded packet label;
- the decision maps cost to compact/full/sham/baseline only after scoring; and
- compact support is refused when compact packet cost exceeds the trace-control cost beyond tolerance.

The make target now fails early unless `RESPONSE`, `EVIDENCE`, and `SCORE_SHEET` are all present, and optionally writes `SUMMARY_OUT`.

## 5. The earlier decision overclaimed its evidence scope

The nominal full control is not a loaded full archive. `packet-delta` contains a few summarized “full public trace excerpt” cues, and all four packet cue sets are visible to the same responder. This design can test bounded semantic discrimination, sham rejection, abstention, and reported effort. It cannot isolate causal compact-versus-full burden or measure the marginal value of loading the actual archive.

The former decision helper could still return `confirm-compact-default-with-escalation` from that design. Current behavior scope-clamps the positive path to:

- `decision_state`: `support-compact-cue-for-bounded-slice`;
- `compact_gate_state`: `remain-narrowed-with-bounded-semantic-support`;
- `global_compact_gate_confirmed`: `false`.

Strong negative evidence can still narrow or reverse the gate. Positive evidence cannot become stronger than the assay that produced it.

## 6. Strict artifact parsing and single-read hash binding

Standard Python JSON parsing accepts duplicate object keys and non-standard constants such as `NaN`. Duplicate keys can create a human/tool interpretation split even when a file hash is stable. The scorer now rejects both conditions recursively.

The response file was also previously read once for its content and later re-read for custody/score hash checks. A concurrent or accidental file change between those reads could bind custody to different bytes than the response object being scored. The scorer now propagates the SHA-256 from the same byte read that produced the validated response object.

## 7. Focused refactor

`tools/priority_zero_external_replay_decision_lib.py` was refactored around one result constructor and explicit score/cost extraction. This removes repeated result dictionaries while preserving historical scorer behavior. The new bounded scope activates only when the current scorer intake sets it; historical rev0368–rev0373 fixtures retain their recorded decision semantics.

`tools/score_priority_zero_external_replay_response.py` now centralizes strict file loading, canonical object/file identity, one-read artifact hashes, per-packet cost reconciliation, and scorer separation. Historical contaminated dry-run summaries remain byte-shape compatible where their scorer contracts did not require rationales or notes.

## Research pressure

The changes are consistent with, but not proved by, external evaluation research:

- Wang et al., *Large Language Models are not Fair Evaluators* (arXiv:2305.17926), reports order/position sensitivity and motivates treating this fixed, co-visible packet order as a residual limitation rather than a causal comparison.
- Wataoka et al., *Self-Preference Bias in LLM-as-a-Judge* (arXiv:2410.21819), and Chen et al., *Do LLM Evaluators Prefer Themselves for a Reason?* (arXiv:2504.03846), motivate removing direct responder self-scoring while retaining a non-claim about broader evaluator bias.
- Karpinska et al., *ConSiDERS—The-Human Evaluation Framework* (arXiv:2405.18638), emphasizes evaluation design and interpretation boundaries; that pressure supports evidence rationales and the decision scope clamp.

These papers do not validate DelayBasin’s assay. They make its prior self-scoring, fixed-order, and overbroad interpretation less defensible.

## Remaining highest risk

The real OQ-0266 object is still absent: a response produced outside this drafting context using only the responder bundle before freeze, followed by a chronology-valid distinct-custodian record and a separate score sheet completed by a scorer distinct from the responder.

A second residual risk is design-level: all packet cues remain co-visible and packet order remains fixed. This overlay prevents that design from confirming the global compact default, but a future causal burden comparison would need isolated or counterbalanced packet exposure and an actual measured full-archive condition.

The correct next substantive move remains import and score the real triplet. Further gate work should occur only for another reproduced admission defect or to replace the co-visible excerpt design with an actually isolated burden trial.

## Validation result

The assembled working tree passed:

- current OQ-0266 synthetic positive path with bounded-support output;
- split-brain custody, self-scoring, missing rationale, boolean score, missing packet cost, cost-sum mismatch, compact-cost disadvantage, and duplicate-key negative canaries;
- all historical Priority-0 scorer contracts exercised by the lint suite;
- the extracted standalone scorer-kit command in the current contract checker;
- cloudtainer preflight with `0` failures and `0` warnings;
- complete lint at `215 / 215`; and
- a whole-tree SHA-256 comparison across `769` files with `0` changed files after lint.

Fresh-extraction package validation is repeated after the outer rev0379 ZIP is built.

## Non-claim

This audit is not a clean external replay result, independent certification, global compact-default confirmation, measured full-archive marginal-value evidence, deletion authority, benchmark authority, or a canonical DelayBasin promotion.
