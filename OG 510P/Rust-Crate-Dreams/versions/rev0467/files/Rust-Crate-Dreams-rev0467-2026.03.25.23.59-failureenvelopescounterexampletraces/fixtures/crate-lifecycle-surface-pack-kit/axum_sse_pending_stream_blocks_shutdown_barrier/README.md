# Axum SSE pending stream blocks shutdown barrier

Simulates a graceful-shutdown path where the accept loop has been told to stop, but a still-pending upstream stream keeps the shutdown barrier from completing.

Why this matters:
- users may read “graceful shutdown support” as “the server stops in bounded time”
- current issue traffic shows that an idle/pending upstream stream can keep the graceful-shutdown future blocked until another event arrives

What this scenario should force:
- a `shutdown-barrier.report` that says the barrier is blocked rather than complete
- an `escape-path.receipt` or dependency receipt that makes the pending upstream wait visible
- a summary note that an upstream wakeup, close, or timeout policy is part of the real stop story
