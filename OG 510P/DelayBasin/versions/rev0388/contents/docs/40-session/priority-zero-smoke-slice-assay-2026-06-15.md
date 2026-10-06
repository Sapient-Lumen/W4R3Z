# Priority-0 smoke-slice assay: core beats archive mass (2026-06-15)

This revision converts the highest-risk unfinished object from a prose obligation into a scored fixture. `rev0360` correctly said the assay should run now; `rev0361` runs the first bounded smoke slice and keeps it deliberately modest.

## Prompt

A future operator receives exactly one packet. Answer: (1) the mission heart, (2) the missing or riskiest object, (3) resolved and live OQ routing, (4) what waste to avoid, (5) the next safe action, and (6) what to abstain from if unsupported.

The scoring surface is `assays/priority-zero-smoke-slice-2026-06-15.json`. It is linted by `tools/check_priority_zero_smoke_slice_contract.py`.

## Result table

| Variant | Score | Operator cost | What it proved |
|---|---:|---:|---|
| No archive | 2 / 16 | 1 min | The prompt alone cannot honestly recover DelayBasin's live mission, `RS-0259`, or `OQ-0252`; abstention is the correct behavior. |
| Minimal core | 14 / 16 | 8 min | The small public packet recovers mission heart, missing assay, routing, anti-review boundary, and next action. |
| Full archive | 15 / 16 | 18 min | Full archive adds contradiction/coldstore context, but for this slice the marginal lift is small and costly. |
| Sham/decoy core | 4 / 16 | 5 min | Fluent but wrong continuity cues are dangerous; accepting them is a negative canary failure. |

## Substantive read

The smoke slice does **not** prove that the archive is self-sufficient. It does prove something narrower and useful: for the immediate continuation task, the minimal core is already doing most of the causal work. The full archive still matters as a recovery and contradiction surface, but using it as the default answer to every reentry question is wasteful until a harder slice shows added value.

The riskiest waste pattern is now clearer: DelayBasin can keep adding currentness-valid surfaces while postponing the thing that would falsify archive mass. The right correction is not deletion by taste. It is a burden-retirement pass that asks every hot surface whether it changed the smoke-slice result, reduced operator cost, preserved a required abstention, or caught a decoy.

## Audit / refactor performed

The prose-only OQ-0252 obligation has been refactored into:

- `assays/priority-zero-smoke-slice-2026-06-15.json` — a machine-readable scored smoke-slice fixture with minimal-core, full-archive, no-archive, and sham/decoy variants.
- `tools/check_priority_zero_smoke_slice_contract.py` — a fail-closed checker that verifies the fixture, score ordering, operator-cost signal, negative canaries, and receipt/ledger routing.
- `SELF-SUFFICIENCY-LEDGER.json#SA-0048` — a current tail row that records the same result as bounded support-availability evidence.

This is a refactor of responsibility, not a new review court. The checker does not judge all semantics; it only prevents DelayBasin from claiming the smoke slice exists while omitting the fixture, the no-archive/sham controls, the operator-cost signal, or the abstention boundary.

A second refactor was applied to `tools/canary_runs_lib.py`: the release canary now treats a partial self-sufficiency score as valid when the packet-test sums are internally consistent, instead of requiring a perfect score. That prevents the canary layer from rewarding inflated smoke-slice numbers and keeps the scorecard useful as evidence rather than ceremony.

## What should change next

`OQ-0253` should force evidence-driven burden retirement. The first candidate criterion is simple: if a hot surface did not improve minimal-core routing, catch a decoy, lower operator cost, or preserve restoration/contradiction checks, it should be demoted, coldstored, or gated behind a harder rotated slice.

## Limits

This was a single-session, non-independent support-availability assay. It is not external benchmark evidence, not a minimality proof, not semantic adequacy certification, and not deletion authority. The next stronger assay should rotate evidence position and filler placement, because recent long-context work makes position-controlled failure a live concern. The memory-agent literature also supports scoring conflict handling and updating separately from answer fluency, and recent freshness/conflict work supports deterministic post-retrieval aggregation over informal LLM judgment.

## Resolution

`OQ-0252` is resolved by `RS-0260`: the first bounded smoke-slice fixture exists and is checked. The live successor is `OQ-0253`: decide what burden to retire, demote, gate, or retest after the first smoke-slice result without turning one smoke test into a review court.
