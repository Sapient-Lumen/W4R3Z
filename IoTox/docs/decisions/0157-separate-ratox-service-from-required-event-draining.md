# ADR 0157: Separate Ratox service from required-event draining

Status: accepted, 2026-08-24.

## Context

The first exact 1,000-sample direct-UDP `bulk-1` matrix attempt completed 599 serialized terminal
renders with an 84.700 ms maximum, then could not observe the next interactive owner command within
its 30-second per-trial bound. The client had a saturated finite-file workload at the same time.
The failure is retained as a failed gate, not latency data.

IoTox deliberately applies bounded backpressure when the transport queue contains only required
events. The sole toxcore owner may therefore wait for the Agent event consumer to free a slot. Before
this decision, that same consumer called periodic Ratox service after each event. Ratox service may
synchronously submit an interactive command to the toxcore owner. Under sustained required file
events, the consumer could consequently wait for the owner while the owner waited for the consumer.
Even without a permanent deadlock, interactive cadence became dependent on the time needed to drain
unrelated required file work.

Dropping incoming chunks, weakening required delivery, making the queue unbounded, or changing the
frozen Ratox v1 frames would hide the boundary instead of repairing it.

## Decision

The Agent retains one ordered transport-event consumer for friendship, protocol, file-transfer, and
runtime projection state. Periodic Ratox host/controller progress moves to one separate Agent service
worker. This is not another toxcore owner: every provider call still crosses the existing classified
owner-command queues and executes on the sole owner thread.

The worker owns Ratox cadence selection and runs at the ADR 0156 active/idle intervals. Local terminal
operations and Ratox-relevant transport events increment a condition-variable generation and wake it.
Generation comparison makes a wake that arrives during service visible before the next timed wait.
All Ratox state effects remain serialized by the existing authority-effect and controller locks.

Shutdown first closes admission, marks both loops stopped, and wakes the service worker. Transport
shutdown cancels any owner command that has not begun; the Agent then joins both workers before
destroying Ratox state. The transport-only event-consumer wake API is removed because local terminal
work no longer belongs on that loop.

## Consequences

- Required file events remain lossless and bounded. Their consumer can keep freeing owner-queue
  capacity while periodic Ratox service waits on an owner command.
- Protocol and file event application remain on their original ordered thread; this change does not
  create a second durable-command, sync, friendship, or transfer-state owner.
- Ratox authority and attachment ordering are unchanged. The additional worker uses the locks already
  required between transport events, local terminal control, sync effects, and authority mutation.
- This repairs one intra-process scheduling dependency. It does not claim a route latency budget,
  provider fairness, or bulk isolation; the exact Sandwurm load matrix still decides those questions.
- Ratox v1 framing, cumulative ACKs, byte windows, replay, authority, and route choice remain frozen.

## Evidence

- The 30-group owned registry passes after the split; five delegated-cgroup capability oracles retain
  their construction-host skips.
- All 45 GCC ThreadSanitizer entries pass after the split; the same five host-capability oracles skip.
- Existing Agent tests require an inbound Ratox frame to produce an outbound result and require
  retained SENDQ work to advance and be revoked through the service path.
- The failed 599-sample raw VM root is disposable diagnostic evidence and is not accepted or exported.
- The exact committed direct-UDP `bulk-1` retry (`pair.1cfwnkj6`) completes 1,000/1,000, closes,
  carries both process-resource intervals, and strictly verifies raw and compact. It accepts this
  liveness repair but fails the independent latency gate at p95 71.698 ms and owner p99 7.114 ms;
  ADR 0158 owns the next local optimization.
