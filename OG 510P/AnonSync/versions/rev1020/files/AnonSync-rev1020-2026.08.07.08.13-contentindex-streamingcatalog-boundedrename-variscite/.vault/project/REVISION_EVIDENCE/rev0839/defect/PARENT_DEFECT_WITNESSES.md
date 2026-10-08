# Parent defect witnesses: rev0838

The sealed parent carried a numeric `process_id`, but its service-start decision never
re-observed that PID and never distinguished PID reuse from the same process life.

The exact parent slices in this directory demonstrate three coupled problems:

1. `parent-heartbeat-pid-write.cpp` writes `getpid()` once as a scalar.
2. `parent-preflight-pidless-stale-policy.cpp` permits re-entry as soon as the wall-clock
   stale horizon is crossed after owner-generation checks; it does not ask whether the
   exact prior process is still alive.
3. `parent-operator-status-lifecycle.cpp` independently reimplements the policy and
   likewise treats a stale heartbeat plus non-live durable owner as sufficient without
   checking process incarnation.
4. `parent-heartbeat-v1-document.cpp` proves the document had no boot/incarnation token.

This matters when a daemon remains alive but misses renewal and heartbeat deadlines, or
when its PID has been recycled. A numeric PID is observational and recyclable. In the
first case, the parent could admit a second daemon while the exact first process still
exists. In the second, a later process could be mistaken for the original if a consumer
tried to use the PID naively.

Rev0839 does not convert process identity into mutation authority. It adds a second,
fail-closed observation that must agree with the stale horizon and durable owner state
before service re-entry is permitted.
