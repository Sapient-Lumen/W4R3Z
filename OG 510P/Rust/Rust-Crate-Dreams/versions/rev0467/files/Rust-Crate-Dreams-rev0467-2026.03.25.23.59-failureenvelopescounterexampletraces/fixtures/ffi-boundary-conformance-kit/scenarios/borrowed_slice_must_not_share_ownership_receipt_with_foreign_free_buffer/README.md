# borrowed_slice_must_not_share_ownership_receipt_with_foreign_free_buffer

This scenario keeps a common C-ABI blur visible:

- a borrowed input slice that is valid only for the duration of the call,
- and a Rust-allocated output buffer that the foreign side must eventually free,

are not the same ownership contract even when both are “just bytes”.
