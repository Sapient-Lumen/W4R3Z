# rev0307 cube deep audit

## Highest-risk seam inspected

The riskiest unfinished work remains the returned-owner-evidence path. The cube can prepare owner packets, route contact clocks, handle returned CSVs, seed review, record decisions, prepare change tickets, and bridge toward activation. But no real owner packet has arrived. That makes every synthetic packet dangerous when it is close enough to the acceptance rail to satisfy hash checks.

`rev0306` correctly blocked returned CSV inputs from checker/release/legacy scratch. The audit for `rev0307` found the next seam: activation receipts verified packet hash lineage, source truth class, reviewer-role count, bounded field counts, and decision-chain integrity, but the source-packet path guard still treated archive scratch too broadly. A byte-identical validator packet in non-field scratch could be named as the activation source packet if it matched the chain hash.

## Correction made

`tools/ft0181_field_guards.py` now restricts activation receipt source packets to either external paths or `scratch/field/ft0181`. Non-field scratch lanes are rejected with `ACTIVATION-RECEIPT-SOURCE-PACKET-BLOCKED`, including checker, release, legacy, smoke, test, and fixture paths.

The validator harness was refactored so synthetic source packets used for activation-path tests are staged under clearly named field-lane validation directories. A new negative regression copies the same bytes into checker scratch and proves the receipt path rejects that packet even though its hash matches.

## What was intentionally not tightened

The broader decision/review/seed chain still has synthetic checker paths in validator mode. Over-tightening those paths would break useful harness coverage and create busywork. The near-acceptance risk is the actual `SOURCE_PACKET` argument to the activation receipt, so this pass closes that seam without adding another doctrine layer.

## Next useful work

The next practical pass should shorten and harden the first human-review-to-decision path: fewer surfaces, clearer source-hash summaries, and simpler operator dockets. Do not add registry families unless a real owner packet exposes a concrete field failure.
