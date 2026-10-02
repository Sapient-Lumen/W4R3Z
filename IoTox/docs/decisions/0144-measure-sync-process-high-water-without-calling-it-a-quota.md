# ADR 0144: Measure synchronization process high-water without calling it a quota

Date: 2026-08-24

Status: accepted

## Context

Directory synchronization already bounds artifact bytes, manifest bytes, entry/path population,
staging, immutable-store growth, and publisher work queues. Those bounds constrain inputs and durable
state, but they are not a measured resident-memory result. Whole-VM consumption would mix IoTox with
the guest kernel, services, page cache, and qualification machinery; one current RSS sample could
also miss an earlier publication, transfer, or projection peak.

Linux exposes `VmHWM` for one process as its lifetime resident-set high-water mark in KiB. It includes
resident anonymous, mapped-file, and shared pages attributed to that process. It is not heap-only,
does not count ordinary unmapped filesystem page cache, and is not a cgroup or physical-memory
reservation.

## Decision

Qualify the current synchronization construction with bounded per-process `VmHWM` observations while
keeping enforcement and measurement claims separate.

- Measure the long-lived production IoTox PID in each guest. Do not use the CLI helper processes,
  VMM RSS, or whole-guest memory.
- Establish each baseline only after the canonical generation-1 tree has converged and activated.
- Publish a linked successor at the namespace's 128-entry ceiling. Its 15 directories, 113 files,
  deep canonical paths, 7,340,226 content bytes, and 7,616,908-byte artifact exercise publication,
  whole-object transfer, verification, and tree projection.
- Record publisher baseline, post-publication, and post-serving high-water; subscriber baseline,
  post-pull, and post-activation high-water; exact baseline deltas; and the pair maximum.
- Require monotonic phase observations and a 65,536 KiB high-water construction ceiling for both
  processes. This is a lab acceptance threshold, not a namespace field or shipped memory limiter.
- Bind every value into both content-free guest receipts and the independently verifiable pair
  manifest. UDP and forced-TCP cells must use the same binary and signed successor identities.

## Consequences

The current direct-UDP cell peaks at 12,924 KiB with a maximum 1,024 KiB post-baseline delta. The
forced-TCP cell peaks at 13,132 KiB with a maximum 1,152 KiB delta. Both are roughly one fifth of the
construction ceiling, and the observed relay-path increase is small in these two samples.

The result closes the named directory peak-memory construction cell without claiming deterministic
allocator behavior, a formal asymptotic proof, heap attribution, page-cache or whole-device demand,
hard runtime enforcement, concurrent namespace/peer/lane maxima, larger configured artifacts,
target-fleet kernels, or an operator SLA. A future hard memory policy requires an explicit product
mechanism rather than reinterpreting this evidence threshold.
