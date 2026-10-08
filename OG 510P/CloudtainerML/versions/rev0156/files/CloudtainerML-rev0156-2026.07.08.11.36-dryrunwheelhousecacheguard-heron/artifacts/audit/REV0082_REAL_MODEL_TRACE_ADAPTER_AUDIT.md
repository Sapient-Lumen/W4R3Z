# Real-model trace adapter audit — rev0082

**Status:** pass_with_blockers

rev0082 hardens the real-model trace adapter around the cached-decode seam: prefill-only rows can no longer self-promote. The adapter still overrides the built-in eager registry key, preserves the eager mask backend, requires an exercised mask-challenge row, exports scale/bias/dense_reference_output, and now requires --decode-steps coverage with valid_key_len padding semantics before a public checkpoint can pass the gate.

Rows in pure mask-challenge adapter/gate fixture: 12

Remaining blocker: run the helper against an immutable public/pretrained HF checkpoint and keep promotion blocked until the gate accepts the bundle and named-hardware timing exists.
