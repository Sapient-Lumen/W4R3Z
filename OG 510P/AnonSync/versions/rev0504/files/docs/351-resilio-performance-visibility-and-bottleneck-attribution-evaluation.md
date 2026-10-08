# Resilio performance visibility and bottleneck attribution evaluation

## Purpose

The archive already had route proof, queue explanation, transfer-method truth, and host-cadence doctrine.
What it still lacked was one explicit comparison document for another ordinary seam:

> when the operator says `why is this slow?`, where does the product itself own the explanation of graph windows, peer-level bottlenecks, disk pressure, and realistic throughput expectations?

Current official Resilio docs are good enough that AnonSync needs a serious answer.
Resilio does not completely hide performance truth.
It exposes live graphs, peer rows, RTT, protocol, disk queue, and a troubleshooting list that names small-file overhead, relay usage, asymmetric peers, security software delay, and closed ports.
That is worth respecting.

## What Resilio gets right

Resilio is still right that:

- performance evidence belongs in-product, not only in logs
- one graph is not enough; peer rows and route/protocol matter too
- disk pressure is a first-class cause and should not be flattened into network blame
- slow transfer can have several materially different causes
- troubleshooting should include counterfactual repairs, not only generic `wait longer` advice

This is better than products that hide all causality behind one spinner.

## What still should not be cloned

The page contract is still scattered.
Current official docs still require the operator to combine at least three article families:

1. **Performance Overview** for graph windows, peer rows, RTT/protocol, and disk queue/load
2. **Slow-speed troubleshooting** for many-small-file penalties, relay usage, asymmetric peers, security software, low-capacity hardware, and port issues
3. **Speed-improvement guidance / preferences** for direct-path preference, predefined hosts, and related repair steps

That means one ordinary answer is still reconstructed from several places:

- what exact time window am I looking at?
- is this number a sample, a trend, or a ceiling?
- which peer is currently holding the transfer back?
- is route class or disk queue the real limiter?
- what improvement is realistically possible versus wishful thinking?

The product substance is good.
The page ownership is still too weak.

## Why this matters for AnonSync

AnonSync should not repeat two common mistakes:

1. **decorative telemetry** — showing motion without owning meaning
2. **post-hoc troubleshooting** — forcing the operator out of the workbench to learn what the telemetry meant

A serious sync product needs one stable public answer to four different questions:

- **metric truth** — what does this graph actually cover?
- **causal truth** — which peer/path is limiting me?
- **resource truth** — is disk pressure local to Sync or mostly external?
- **expectation truth** — what speed should I honestly expect from this workload and topology?

## Replacement pages in this revision

This revision adds four fixed pages:

- `352` — Activity metrics
- `353` — Peer connection table
- `354` — Disk pressure
- `355` — Throughput expectation

Together they replace article-shaped observability with product-owned causality.

## The doctrinal line

Borrow directly:

- live graphs
- peer-level route / RTT evidence
- disk queue visibility
- explicit admission that workload shape and route class change performance

Do not clone directly:

- graphs whose window meaning is implicit
- peer tables that are visible but not causally ranked
- disk telemetry that does not separate Sync contribution from host-wide contention
- troubleshooting lists that name many causes without one stable in-product page tying them together

## Conclusion

The correct AnonSync response is not `hide less telemetry`.
It is stronger than that:

> keep performance truth public, but make every visible graph, peer row, and slowdown verdict resolve into one stable explanation surface that says what is being measured, why it is slow, what counterfactual route or resource change would help, and what improvement is realistically bounded by workload shape.
