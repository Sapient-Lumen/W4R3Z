# Real-model trace adapter audit — rev0080

**Status:** pass_with_blockers

rev0081 closes the most dangerous rev0080 seam: it no longer creates a custom AttentionInterface backend that can lose the causal mask. The adapter overrides the built-in eager registry key, preserves the eager mask backend, requires an exercised mask-challenge row, exports scale/bias/dense_reference_output, and still blocks promotion until a real public checkpoint passes the gate.

Rows in pure mask-challenge adapter/gate fixture: 12

Remaining blocker: run the helper against an immutable public/pretrained HF checkpoint and keep promotion blocked until the gate accepts the bundle and named-hardware timing exists.
