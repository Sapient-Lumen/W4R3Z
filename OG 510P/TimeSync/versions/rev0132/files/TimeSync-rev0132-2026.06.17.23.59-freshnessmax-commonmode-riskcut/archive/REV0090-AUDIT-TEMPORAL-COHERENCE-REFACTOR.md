# rev0090 audit — temporal-coherence validator refactor

The main validator remains intentionally comprehensive, but rev0090 extracts the new timestamp-coherence logic into `tools/temporal_coherence.py`.

This keeps the high-risk freshness rules testable and reusable without waiting for a full validator split. The next validator refactor should move existing interval ordering, lifecycle timestamp, replay-anchor freshness, and policy-reference observation checks into the same module family.
