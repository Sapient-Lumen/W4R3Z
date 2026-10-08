# JoinHandle drop detaches background task

Simulates a crate that returns a handle to a background task and then drops the `JoinHandle` internally or tells users to drop it when they are done.
The lifecycle contract should not pretend that dropping the handle is the same thing as stopping the task.

Why this matters:
- Tokio documents that dropping a `JoinHandle` detaches the task and loses its output;
- downstream users need to know whether drop means “cleanup happened” or only “you no longer hold the receipt for the task”.

What this scenario should force:
- a stop-semantics receipt such as `drop_detaches`
- a teardown-evidence class no stronger than `shutdown_requested_only` unless separate proof exists
- a summary note that explicit close/join/drain is required for clean stop
- a doctor warning such as `drop_detaches_without_explicit_summary`
