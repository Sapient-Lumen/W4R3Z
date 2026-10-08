> **Superseded evidence-status notice (rev0337):** This historical report treated archive-generated deterministic fixtures as implementation-grade evidence. Its implementation, promotion, or finalization counts demonstrate schema conformance only, not externally observed facts or authority. Use [the rev0337 truth-boundary report](evidence-truth-boundary-release-lineage-refactor-rev0337.md) for current status.

# Decision output materialization hold-reasons refactor — rev0336

## Purpose

rev0335 added a promotion gate after replay. The next risk was output ambiguity: promotion packets said which cases could be finalization-ready, but the cube still did not emit a final decision-output artifact that cleanly separated promoted determinations from held determinations.

rev0336 adds that boundary. It materializes one case-level decision-output packet per answer packet. The packet is explicitly non-doctrinal and stores hashes, statuses, ordered obligations, blocked moves, and hold reasons rather than raw authority text, raw evidence records, jurisdiction conclusions, or model-output snapshots.

## Added runtime boundary

`tools/materialize_decision_outputs.py` consumes answer packets, a replay ledger, and a decision-promotion packet. It emits `promotion_gated_decision_output_packets` with runtime status `decision_output_packets_materialized`.

For promoted cases, the packet carries:

- ordered route IDs and recommended sequence,
- dominant disposition,
- default moves and blocked moves,
- actor assignments,
- adapter summaries,
- ledger hash,
- evidence-bundle hash,
- producer-contract manifest hash,
- case-promotion hash,
- per-adapter record hashes, and
- a non-doctrine warning.

For held cases, the packet carries the same routing and evidence hashes plus:

- promotion reasons,
- blocked adapters,
- cannot-finalize markers,
- record errors when present, and
- a direct instruction not to issue a final determination from that evidence state.

`tools/audit_decision_output_packets.py` independently rebuilds the implementation-shaped evidence bundle, materializes decision outputs, then verifies empty evidence, strict interface fixtures, and replay-tampered evidence finalize zero cases.

## Audit results

- Answer packets checked: **122**
- Adapter checks / execution records: **1724**
- Implementation finalized cases: **83/122**
- Implementation held cases: **39/122**
- Empty-evidence finalized cases: **0/122**
- Strict interface-fixture finalized cases: **0/122**
- Replay-tamper mismatches detected: **5172**
- Replay-tamper finalized cases: **0/122**
- Raw evidence stored in decision outputs: **false**

Decision-output status counts:

- `finalized_from_promoted_replay_clean_strict_evidence`: **83**
- `held_pending_satisfied_replay_clean_strict_evidence`: **39**

## Substantive correction

The cube now distinguishes six states that previously could blur together:

1. a route is relevant,
2. a disposition requires adapter evidence,
3. registered evidence is supplied,
4. strict execution accepts or blocks each adapter record,
5. replay and promotion say whether the case can be finalization-ready, and
6. a final decision-output packet either finalizes the case under the supplied evidence bundle or holds it with explicit reasons.

This prevents a downstream user from treating “promotion metadata exists” as the final answer. The final answer boundary is now itself auditable.

## Refactor discipline

This revision adds no routes, axes, or source IDs. It adds a narrow output materialization surface and integrates it into the semantic release path.

The materializer deliberately refuses to store raw evidence-like fields such as `raw_evidence`, `evidence_snapshot`, `authority_text`, or `model_output_snapshot`. Decision outputs carry only hashes and summarized obligations.

## Remaining risk

The next frontier is replacing implementation-shaped reference evidence with real external producer runs while preserving this output discipline: final decision-output packets should remain hash-bound and non-doctrinal even when authority retrieval, jurisdiction review, microdata, delivery-capacity inputs, incidence assumptions, and expert no-go review records are supplied by real producers.
