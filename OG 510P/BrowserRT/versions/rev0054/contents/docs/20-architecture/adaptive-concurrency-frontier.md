# Adaptive concurrency frontier

Revision: rev0028

## Policy ladder

```txt
L0 static limit
L1 static watermarks
L2 fake-latency adaptive controller
L3 provider-latency adaptive controller
L4 lane-level adaptive controller
L5 fair adaptive controller
L6 mesh-wide adaptive controller
```

Current proof: L2.

## Required invariants

Rejected acquisition must not mutate in-flight counts, lease tables, or window samples. Provider-unhealthy state rejects low-priority work until recovery is explicit.

- Rejecting an acquire must not mutate in-flight count or leases.
- A completed/released lease must decrement in-flight count exactly once.
- A healthy latency window can increase the limit.
- A high-delay window can decrease the limit.
- Timeout/error windows must back off.
- Critical bypass must stay bounded by the hard maximum.
- Provider health must be traceable.
- Probe windows must be visible because they intentionally distort capacity.

## Controller inputs

Current fake inputs:

```txt
latencyMs
outcome
priority
weight
provider health
forceProbe
```

Future real inputs:

```txt
OPFS request latency
worker queue delay
mailbox residence time
Long Task observations
GPU readback time
quota pressure
hidden-tab status
```

## Controller outputs

```txt
admitted
rejected-limit
rejected-hard-limit
rejected-provider-health
admitted-critical-bypass
limit increase
limit decrease
probe min limit
```

## Trace contract

Every decision must explain:

```txt
previous limit
next limit
sample count
latency summary
timeout/error count
reason
provider health
in-flight count
```

## Non-claims

No production tuning, no exact external algorithm implementation, no browser workload latency, no fairness guarantee, no throughput claim, and no cross-browser behavior.
