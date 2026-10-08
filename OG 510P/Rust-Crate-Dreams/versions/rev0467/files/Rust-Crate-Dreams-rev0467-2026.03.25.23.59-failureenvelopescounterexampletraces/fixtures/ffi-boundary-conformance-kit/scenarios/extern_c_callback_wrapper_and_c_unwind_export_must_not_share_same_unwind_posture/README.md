# extern_c_callback_wrapper_and_c_unwind_export_must_not_share_same_unwind_posture

This scenario keeps two different boundary stories separate:

- an `extern "C"` callback wrapper that catches unwinding Rust panics and translates them into an error path,
- and a deliberately unwind-capable export that uses an unwind ABI and documents that posture explicitly.

Both involve non-local control flow, but they are not the same unwind contract.
