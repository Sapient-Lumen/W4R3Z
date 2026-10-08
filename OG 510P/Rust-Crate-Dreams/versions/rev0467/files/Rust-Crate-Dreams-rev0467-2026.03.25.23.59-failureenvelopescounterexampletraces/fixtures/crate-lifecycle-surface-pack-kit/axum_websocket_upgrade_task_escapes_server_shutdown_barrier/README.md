# Axum WebSocket upgrade task escapes server shutdown barrier

Simulates a crate or framework surface where a server exposes a graceful-shutdown future, but upgraded WebSocket work is spawned onto a path that is **not** governed by that completion event.

Why this matters:
- Tokio/axum users can reasonably read “graceful shutdown completed” as “connection work is done”.
- Current issue traffic shows that upgraded WebSocket work may continue running after the server graceful-shutdown future resolves.

What this scenario should force:
- a `shutdown-barrier.report` that says the barrier is weaker than full protocol completion
- an `escape-path.receipt` that makes the upgraded task visible
- a summary note that a shared cancellation token or explicit connection-close route is still required
