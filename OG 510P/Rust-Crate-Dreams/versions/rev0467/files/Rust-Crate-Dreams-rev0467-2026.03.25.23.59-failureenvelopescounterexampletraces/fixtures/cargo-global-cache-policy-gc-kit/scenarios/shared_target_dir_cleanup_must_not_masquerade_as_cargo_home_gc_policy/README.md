# Scenario: shared target-dir cleanup must not masquerade as Cargo-home GC policy

This scenario exists so **P-0480** does not silently treat workspace/shared `CARGO_TARGET_DIR` cleanup as the same surface as Cargo-home garbage collection.

The key claim is that a plan about `target/` or build-dir artifacts needs a **cache-surface receipt** that keeps it separate from Cargo-home registry/git caches.
