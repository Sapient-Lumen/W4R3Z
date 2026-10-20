# 0003: Race Real-Time Data; Do Not Guess Terminal Output

Status: accepted

## Context

AnonSSH's public-overlay typing latency has a long tail even after bulk isolation,
priority queues, independent SSH streams, and protected low-latency lanes. The current
product launches external OpenSSH over `BondedStream`. The bond therefore sees encrypted
SSH records, not keystrokes, terminal echo state, passwords, or screen updates.

[Mosh](https://mosh.org/) improves perceived latency with a client terminal model and
server-state reconciliation. It confirms prediction behavior and starts new prediction
epochs around ambiguous input. [Eternal Terminal](https://github.com/MisterTea/EternalTerminal/blob/master/docs/protocol.md)
primarily preserves a server terminal process and exchanges sequenced catch-up buffers
after reconnect; it is not a safe precedent for blind local echo below SSH encryption.

Replication and first-copy elimination are established latency/reliability tools; the
[IETF DetNet PREOF specification](https://www.rfc-editor.org/info/rfc9566/) describes
packet replication, elimination, and ordering. ABP
already authenticates offsets and eliminates exact retransmission duplicates, so it can
apply the same general idea without changing its wire grammar.

## Decision

The product races eligible Realtime data and Interactive chunks no larger than 2 KiB
over the two active protected lanes. A mixed Tor/I2P bond reserves the best eligible
lane from each provider so the race does not depend on one overlay; a homogeneous bond
reserves its two best independent lanes. Provider grouping supplements rather than
replaces each router's unique failure domain. Both copies have one stream offset and
share one immutable payload allocation. Sender credit and retained state are charged
once. The first authenticated copy advances reassembly; the other is discarded and
acknowledged.

Redundancy is bounded to one shadow copy, excludes control and bulk, and degrades to one
copy when no protected standby exists. Shadow queue saturation is telemetry, not an
application error. The receiver returns an immediate acknowledgement on the winning
ingress lane when possible so path learning can credit the actual winner.
Tokio sessions enable winner-attributed redundancy only for negotiated ABP v3 or newer;
legacy v1/v2 sessions remain single-copy because those peers may route acknowledgements
over an unrelated lane.

AnonSSH will not predict or locally echo opaque SSH bytes. A future predictive mode must
own a client PTY and terminal screen model plus a corresponding server terminal/session
adapter above encryption, with explicit correction and secret-input behavior.

The bond's interactive optimization target is consistent physical delivery, not
LAN-like perceived response. Retained quiet public-overlay evidence measured about
463 ms p50 and 595 ms p95, while isolated typing under a concurrent multi-client bulk
transfer measured 513 ms p50 and 770 ms p95. These measurements are descriptive rather
than an SLA, but they establish the practical engineering boundary: continue work that
reduces avoidable queueing, regressions, or pathological tails, and reject additional
bond complexity whose only proposed benefit is hiding unavoidable overlay propagation.
Throughput scaling, warm-path reuse, recovery, and bounded latency under contention
remain product priorities.

## Consequences

- Tiny interactive traffic spends up to twice its payload bytes to reduce path-jitter
  tails; bulk throughput remains single-copy.
- Existing ABP peers remain wire compatible because duplicate offsets already have exact
  replay semantics.
- Runtime and endurance evidence must report accepted and dropped shadow frames and tag
  whether redundancy was enabled.
- This improves actual delivery latency but cannot make a physical round trip appear
  instantaneous. Product claims must keep that distinction explicit.
- Sub-second quiet typing is a reasonable observed operating envelope, not a guaranteed
  threshold. Provider geography, circuit construction, congestion, and tunnel churn can
  produce materially slower responses.
- Future LAN-like perceived typing is a separate terminal-product decision. It must not
  be implemented as another transport heuristic or used to hold up the bonded transport.
- Retained public-overlay evidence protects one lane from each provider and shows both
  can win, but Tor wins most quiet races. Provider diversity is therefore a resilience
  decision, not a claim that I2P usually reduces the fastest-path latency.
