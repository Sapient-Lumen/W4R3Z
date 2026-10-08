# spawned future without `in_current_span` creates a lineage gap

This scenario captures a codebase where `tracing` spans exist, but spawned futures do not consistently propagate the current span.
The important truth is that a visually rich trace can still have causal blind spots.

What the report should prove:

- whether span propagation was explicit or partial,
- whether spawned-task lineage is missing,
- and that the support summary calls the bundle partial rather than complete.
