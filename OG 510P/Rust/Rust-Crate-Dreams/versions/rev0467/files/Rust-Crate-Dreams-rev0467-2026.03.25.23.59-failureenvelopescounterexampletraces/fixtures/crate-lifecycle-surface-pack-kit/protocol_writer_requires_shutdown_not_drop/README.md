# Protocol writer requires shutdown, not just drop

Simulates a stream / protocol writer where ordinary writes are not the same thing as graceful teardown.
The lifecycle contract should distinguish writing bytes from completing the protocol-level shutdown handshake.

Why this matters:
- Tokio distinguishes cancel-safe writes from `write_all` and also documents `shutdown` on `AsyncWrite` as the hook for graceful protocol shutdown;
- downstream users may otherwise assume that dropping the writer or finishing writes implies graceful teardown.

What this scenario should force:
- a shutdown-obligation report that marks `shutdown` as required or strongly recommended
- a teardown-evidence report such as `protocol_shutdown_observed` or `flush_then_shutdown_observed`
- a summary note that `drop` is weaker than graceful protocol shutdown
- a doctor warning such as `graceful_shutdown_claim_without_teardown_evidence`
