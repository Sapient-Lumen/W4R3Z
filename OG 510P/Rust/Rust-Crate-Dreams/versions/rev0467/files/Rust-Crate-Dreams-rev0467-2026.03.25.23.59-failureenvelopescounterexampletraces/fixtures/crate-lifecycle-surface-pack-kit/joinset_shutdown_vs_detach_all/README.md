# JoinSet shutdown versus detach-all

Simulates a crate that manages a group of tasks internally with Tokio `JoinSet` semantics.
The lifecycle contract should keep `drop`, `detach_all`, and `shutdown()` visibly separate.

Why this matters:
- Tokio documents that dropping a `JoinSet` aborts all tracked tasks.
- Tokio also documents that `detach_all` keeps those tasks running, while `shutdown()` aborts and waits for completion.

What this scenario should force:
- a stop-semantics receipt that distinguishes drop-aborts, detach-keeps-running, and shutdown-waits
- a drain recipe that names the supported clean-stop path explicitly
- a summary note that `detach_all` is not the same thing as graceful shutdown
