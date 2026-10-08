# Scenario: static embedded executors are not the same runtime profile

This scenario exists to stop another common flattening move:

> “Embassy, RTIC, and Tokio are all just async runtimes.”

They are not the same support surface.
Embassy documents static tasks, no `alloc`, integrated timers, and optional multi-priority executors.
RTIC documents interrupt-priority scheduling, timer queues, shared-stack memory posture, and compile-time deadlock-freedom claims.
