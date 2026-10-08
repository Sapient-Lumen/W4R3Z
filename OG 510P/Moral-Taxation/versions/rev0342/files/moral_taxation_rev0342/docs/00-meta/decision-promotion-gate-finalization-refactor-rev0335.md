> **Superseded evidence-status notice (rev0337):** This historical report treated archive-generated deterministic fixtures as implementation-grade evidence. Its implementation, promotion, or finalization counts demonstrate schema conformance only, not externally observed facts or authority. Use [the rev0337 truth-boundary report](evidence-truth-boundary-release-lineage-refactor-rev0337.md) for current status.

# Decision promotion gate finalization refactor — rev0335

## Purpose

rev0334 made strict adapter evidence decisions replay-checkable. The next risk was promotion control: a replayable evidence execution could still be confused with a decision that is finalization-ready. That is especially dangerous for no-go harms, strict interface fixtures, stale evidence, or replay drift.

rev0335 adds a post-replay promotion gate. It consumes replay-ledger records and emits one case-promotion packet per answer case. It does not store raw authority text, jurisdiction conclusions, model outputs, or new route doctrine.

## Added runtime boundary

`tools/promote_decision_release.py` builds a `decision_promotion_gate_packet` from an evidence replay ledger. A case may promote only when:

- the replay ledger has current runtime status and a top-level ledger hash,
- same-bundle replay has zero mismatches,
- every adapter record has adapter, evidence, producer-contract, decision-trace, and result hashes,
- every adapter record has evidence present and a non-doctrine warning,
- every adapter record is satisfied, and
- no record carries a cannot-finalize marker.

`tools/audit_decision_promotion_gate.py` independently rebuilds implementation-grade model/source and authority/source/intake/evidence bundles, builds the replay ledger, runs the promotion gate, then verifies missing evidence, strict interface fixtures, and tampered replay comparisons hold all cases rather than promoting them.

## Audit results

- Answer packets checked: **122**
- Adapter execution records: **1724**
- Implementation promoted cases: **83/122**
- Implementation held cases: **39/122**
- Satisfied adapter records: **1672/1724**
- Blocked adapter records: **52/1724**
- Empty-evidence promoted cases: **0/122**
- Strict interface-fixture promoted cases: **0/122**
- Tamper replay mismatches detected: **5172**
- Tamper-promotion promoted cases: **0/122**

## Substantive correction

The cube now distinguishes five states that previously could blur together:

1. an adapter requires evidence,
2. a registered producer supplies evidence,
3. strict execution accepts or blocks the evidence,
4. the execution decision replays cleanly, and
5. a case is actually promotable to final-disposition readiness.

This prevents a validated-but-blocking no-go screen, a fixture bundle, or a replay mismatch from being treated as final clearance.

## Refactor discipline

This revision adds no routes, axes, or source IDs. It adds a narrow promotion-control surface and integrates it into the semantic release path. The new packet stores hashes, statuses, cannot-finalize markers, and non-doctrine warnings, not live-law conclusions or model outputs.

## Remaining risk

The next frontier is true external producer replacement: live authority retrieval, calibrated jurisdictional model inputs, delivery-capacity data, incidence assumptions, and expert no-go review records should arrive through the existing evidence boundary and then be replayed and promotion-gated before use.
