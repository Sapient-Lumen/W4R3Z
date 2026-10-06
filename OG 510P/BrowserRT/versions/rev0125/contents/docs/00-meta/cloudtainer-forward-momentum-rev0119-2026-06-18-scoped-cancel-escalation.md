# Cloudtainer forward momentum — rev0121 scoped cancel escalation

Rev0119 is a substance-first pass against the highest leftover runtime risk from rev0118: cancelled work could still execute indefinitely if user worker code ignored its signal. The new path does not pretend JavaScript can preempt arbitrary code. Instead it makes the tradeoff explicit: cooperative cancellation remains the default, and callers may opt into terminating the whole WorkerAgent after a grace window.

## Product changes

- `OperationScope` is now the product owner for child scopes, resources, cleanup callbacks, abort propagation, snapshots, and close reports.
- `BoundedChannel` waits and runtime factories can attach to a scope.
- `WorkerAgent.call()` now accepts `scope`, `terminateOnCancel`, and `cancelGraceMs`.
- Worker shells still support per-call cooperative `AbortController`s.
- A non-cooperative `busy-loop` test op proves the escalation path terminates abandoned stuck work.

## Cube audit/refactor

The package boundary was too wide: `./internal` exposed the full runtime module as a consumer surface. Rev0119 removes that export and extends both public API and installed-package smoke audits to fail if it returns. This is a real surface shrink, not another registry entry.

## Remaining risk

`terminateOnCancel` kills an agent, not a single call. Long-lived shared agents need higher-level policy before using it broadly. The next useful cut is to make the golden workload use `OperationScope` end-to-end across admission, worker transform, storage lane, and teardown.
