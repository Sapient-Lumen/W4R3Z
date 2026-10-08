# rev0063 speed-envelope decomposition audit

rev0063 adds a native CPU speed-envelope replay over the local tiny-trained Q/K/V packet. It is deliberately stricter than the rev0062 materialized histogram replay in one respect and looser in another:

- stricter: QK score construction remains inside the timed native replay;
- looser: exact Top-p 0.96 support is supplied as an oracle/free-selector upper bound.

This isolates whether the next useful work should be deployable selector optimization or whether dense QK/value math leaves no measured headroom. The artifact therefore cannot promote a sparse-attention mechanism. It can only bound opportunity.

Fresh artifact: `artifacts/probe-results/REV0063_TRACE_PACKET_SPEED_ENVELOPE.json`.

Key fields:

- `oracle_topp96_qk_included_speedup_vs_dense`
- `oracle_topp96_value_only_speedup_vs_dense_value_only`
- `qk_scores_only_fraction_of_dense_online_time`
- `oracle_topp96_quality_rate`
- `oracle_topp96_mean_selected_fraction`

Claim boundary:

- local tiny-trained trace only;
- not public/pretrained evidence;
- not GPU/fused timing;
- exact Top-p support is oracle supplied;
- all QK scores are still computed.
