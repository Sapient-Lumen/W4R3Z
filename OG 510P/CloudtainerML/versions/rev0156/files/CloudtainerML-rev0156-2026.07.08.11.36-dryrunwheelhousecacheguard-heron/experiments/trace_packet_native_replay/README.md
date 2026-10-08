# rev0061 trace-packet native replay

This experiment measures the rev0060 learned trace packet with native C++ loops. It is intentionally scoped to a **materialized-score CPU replay**: scores are already present in the packet, so this is not a QK-compute benchmark, not a fused kernel, and not public/pretrained model evidence.

The purpose is to veto proxy-only promotion. rev0060 estimated that score-storage-allowed sparse dispatch might be faster on the learned packet. rev0061 asks whether the same packet still looks attractive once the dense and histogram paths are executed with the same native score-consumption/value-accumulation loops.
