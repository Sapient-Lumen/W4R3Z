# Tokio fs async surface does not upgrade commit contract

Simulates a crate that advertises stronger persistence semantics simply because it performs its writes through `tokio::fs`.

Why this matters:
- Tokio documents that its ordinary file IO uses `spawn_blocking` behind the scenes.
- That changes scheduling and performance posture, but by itself does **not** create a stronger save/commit/durability contract than the underlying ordinary file operations.
- A persistence-surface crate should therefore keep async ergonomics separate from durability claims.

What this scenario should force:
- a durability-boundary report that stays tied to the actual file-write path, not the async wrapper
- a doctor warning such as `tokio_async_surface_presented_as_stronger_commit`
- a summary that distinguishes runtime ergonomics from persistence guarantees
