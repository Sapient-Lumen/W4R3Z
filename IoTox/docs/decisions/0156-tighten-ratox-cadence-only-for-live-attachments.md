# ADR 0156: Tighten Ratox cadence only for live attachments

Status: accepted, 2026-08-24.

## Context

After ADR 0155 removed evidence collection from the measured interval, a clean 1,000-sample
direct-UDP idle cell still rendered at p50 62.107 ms, p95 83.115 ms, p99 86.936 ms, and maximum
91.020 ms. It delivered every sample and kept owner interactive queue p99 at 0.511 ms, so the
provisional 50 ms p95 miss was not owner-class congestion or PTY execution.

Two disposable diagnostic cells separated the remaining delay. Capping toxcore iteration at 5 ms
while leaving Agent Ratox service at 20 ms improved render p95 to 59.230 ms but still missed the
target. Capping both at 5 ms produced p50 21.241 ms, p95 32.000 ms, p99 47.643 ms, maximum 78.324 ms,
zero 250 ms misses, and owner queue p99 0.689 ms. These diagnostic roots and their dirty binaries
were deliberately not accepted as qualification evidence.

The transport provider has no network-descriptor wakeup interface. The owner thread already has a
condition-variable wake path for local commands, but the Agent event consumer independently slept
up to 20 ms before servicing Ratox PTY work. A permanent 5 ms process-wide poll would buy latency by
forcing up to 200 idle wakeups per second on every enabled device, including devices with no live
terminal.

## Decision

An enabled Ratox host or controller has two explicit cadence classes:

- idle: retain the configured ordinary toxcore maximum iteration interval and the existing 20 ms
  Ratox service poll;
- active: while a host attachment, host close/outbound transition, or local controller
  open/attached/resume/close transition is live, cap toxcore iteration at the lesser of the ordinary
  cap and 5 ms and poll Ratox service at 5 ms.

Successful local terminal OPEN, INPUT, RESIZE, output acknowledgement, DETACH, and CLOSE operations
wake the Ratox service worker immediately. The wake is generation-coalesced and carries no synthetic
transport event. Entering active mode wakes the toxcore owner thread so a newly tightened maximum
takes effect without waiting for its former sleep. Returning to idle restores the ordinary
configured maximum. ADR 0157 subsequently separates this worker from the ordered transport-event
consumer so required file-event backpressure cannot suppress its cadence.

The defaults are configurable as `--ratox-active-service-ms` (1..20) and
`--ratox-active-iterate-ms` (1..1000). Runtime status publishes both configured values and whether
active mode is currently selected. Sandwurm Ratox cells retain a process-incarnation-fenced resource
interval for each role, including CPU ticks, context switches, faults, resident memory, descriptors,
I/O counters, transport iterations, and the idle cadence at both interval boundaries.

## Consequences

- The latency cost is paid only while interactive state is live; idle Ratox-enabled devices preserve
  their prior transport and service cadence.
- OPEN may begin under the ordinary idle cap. Once the controller/host transition is observable,
  subsequent interactive service uses the active cap.
- A user's smaller ordinary transport cap is never widened by Ratox active mode.
- The two active intervals are operator-visible experimental controls, not independent claims that
  every kernel, route, or power envelope supports the default.
- Resource intervals measure process behavior over complete cells; they are observations, not hard
  CPU, RSS, descriptor, or energy quotas.
- Ratox v1 frames, cumulative acknowledgement semantics, authority, replay, and route selection are
  unchanged.

## Evidence

- The owned transport tests dynamically tighten a running toxcore owner from 20 ms to 5 ms and
  reject out-of-range caps. Agent Ratox tests exercise independently woken service progress without
  adding a transport event.
- CLI, runtime projection, compact-export, strict-verifier, and process-resource capture tests are
  included in the 30-group owned registry.
- Exact-commit clean idle cells passed on direct UDP and forced TCP. Direct UDP rendered 1,000/1,000
  samples at p50 16.345 ms, p95 23.943 ms, p99 31.308 ms, and maximum 52.402 ms. Forced TCP rendered
  1,000/1,000 at p50 88.810 ms, p95 99.010 ms, p99 128.852 ms, and maximum 131.091 ms. Their remote
  stage-to-output p95 values were 12.764 ms and 11.515 ms respectively, localizing most forced-TCP
  median cost outside remote Ratox queue/PTY service. Loaded qualification remains separate.
