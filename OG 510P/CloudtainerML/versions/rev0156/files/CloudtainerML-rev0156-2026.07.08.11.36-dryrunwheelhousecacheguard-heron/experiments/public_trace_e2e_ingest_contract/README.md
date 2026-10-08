# Frozen rev0073 public trace E2E ingest contract

This is a retained historical negative-control contract. The runner is pinned to `rev0073`; it must not inherit the live cube revision or create a later-revision artifact.

The rev0073 probe established that detached JSON provenance was insufficient and that local fixtures must remain non-public. Its v1 self-attestation contract is superseded by the rev0076 tensor-stage, score-semantics, recomputed-parity, and immutable-revision requirements.

Historical reruns belong in a scratch copy. Use the rev0076 capture helper, gate, and acceptance preflight for current work.
