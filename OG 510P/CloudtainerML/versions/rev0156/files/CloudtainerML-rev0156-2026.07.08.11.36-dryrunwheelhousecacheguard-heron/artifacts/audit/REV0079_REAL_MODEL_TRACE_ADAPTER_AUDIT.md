# Real-model trace adapter audit — rev0079

**Status:** pass_with_blockers

rev0079 replaces the raw-projection-only HF helper with a verified Llama eager-attention adapter path: capture after RoPE, export scale/bias and dense_reference_output, and require recomputed dense parity before self-attesting as public/pretrained. This is adapter progress, not actual public-model evidence, because no public checkpoint was loaded here.

Rows in pure adapter/gate fixture: 12

Remaining blocker: run the helper against an immutable public/pretrained HF checkpoint and keep promotion blocked until the gate accepts the bundle and named-hardware timing exists.
