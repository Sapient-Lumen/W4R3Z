# `spawn_blocking` abort is not guaranteed

Simulates a crate that exposes an abort handle for work that may already be running on Tokio's blocking pool.
The lifecycle contract should not imply that issuing `abort()` guarantees the blocking work has stopped.

Why this matters:
- Tokio documents that running `spawn_blocking` tasks cannot be aborted once they have started.
- downstream users need to know whether `abort` is a strong stop path or only a best-effort request.

What this scenario should force:
- a stop-semantics receipt such as `blocking_work_not_abortable` or `abort_best_effort`
- teardown evidence no stronger than `manual_review_required` unless completion was separately observed
- a doctor warning such as `abort_claim_exceeds_blocking_work_evidence`
