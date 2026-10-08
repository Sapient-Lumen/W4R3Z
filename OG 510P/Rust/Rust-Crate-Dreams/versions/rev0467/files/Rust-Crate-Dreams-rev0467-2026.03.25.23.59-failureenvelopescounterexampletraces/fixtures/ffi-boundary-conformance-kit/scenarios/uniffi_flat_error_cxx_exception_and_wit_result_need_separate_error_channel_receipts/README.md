# UniFFI flat error, CXX exception, and WIT result need separate error-channel receipts

This scenario exists to stop multiple boundary families from quietly claiming the same fallibility model.

The current substrate already shows materially different error channels:

- UniFFI can expose Rust `Result<T, E>` errors as foreign exceptions, and flat enum exposure can drop associated data.
- `cxx` maps Rust-side fallibility and C++ exceptions through explicit `Result` / exception machinery.
- WIT exposes `result<ok, err>` as an interface-level contract with canonical ABI lowering.

A worthy contract crate should emit separate error-channel receipts for those surfaces rather than one fake “returns errors” status.
