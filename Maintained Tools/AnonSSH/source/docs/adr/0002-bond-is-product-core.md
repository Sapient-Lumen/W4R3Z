# 0002: Make the bond the product core

Status: accepted

## Decision

AnonSSH's product core is a reusable, dynamically scheduled striped transport. SSH is
one consumer of that transport, not the transport's organizing abstraction. The
existing direct Tor and I2P recovery paths remain available while the bonded path is
operated and refined.

The bond is a custom userspace protocol over reliable lanes supplied by Tor SOCKS, I2P
SAM, loopback tests, or future stream transports. It borrows established multipath
ideas such as a connection-level sequence space, authenticated lane joins, selective
acknowledgements, and cross-lane retransmission, but it does not depend on kernel MPTCP,
QUIC, or another off-the-shelf multipath wire protocol.

The native abstraction is a long-lived bonded session carrying multiple logical
streams. A byte-stream facade supports SSH and legacy applications. Long-lived sessions
keep expensive anonymous-network setup warm, provide enough queued work for useful
striping, and allow applications to identify real-time and bulk streams separately.

## Product interfaces

One bond architecture serves or is intended to serve three interfaces:

1. A Rust library exposing bonded sessions, streams, listeners, and pluggable lane
   providers.
2. Named local forwarding for unmodified applications and a public local transport
   socket for native applications.
3. A stdin/stdout pipe for OpenSSH ProxyCommand and command-line composition.

The Rust stream, OpenSSH pipe, and named local TCP forwarding interfaces are shipped.
Unix-socket forwarding remains deferred. The distinct owner-only ALP socket and static
symbolic peer-service protocol selected by ADR 0005 are shipped; dynamic registration
and maintained language clients remain pending. Current implementation status lives in the
[specification ledger](../../specs/spec_ledger.json) and
[`application-interfaces.md`](../context/application-interfaces.md).

An arbitrary internet-exit SOCKS proxy, a TUN device, and system-wide interception are
deferred. Language clients for the designed ALP socket are in scope because they expose
striped delivery without a process ABI or duplicated transport implementation.

## Scheduling policy

High sustained goodput and protected real-time latency are coequal scheduler
requirements. The scheduler continuously estimates each lane's round-trip time,
acknowledged delivery rate, queued work, and health. It assigns each chunk to the lane
with the earliest predicted delivery time; naive round-robin is forbidden because an
uneven lane can create unbounded reordering and head-of-line delay.

At least one healthy low-RTT lane is dynamically reserved for control and real-time
traffic whenever another healthy lane can carry bulk data. Bulk traffic cannot enter
the reserved pool in that state. If no non-reserved lane remains, bulk may use the
reserved lane because no scheduler can provide physical isolation on a single path.
Chunks already committed to an underlying reliable stream cannot be preempted, so bulk
chunk size and per-lane queued bytes must remain bounded. New bulk chunks therefore use
one allocation-free lane-and-size decision: per-lane bandwidth-delay estimates propose
16-64 KiB payloads, while queue delay, selective-acknowledgement gaps, and timeouts drive
bounded backoff. Control and typing-sized data do not use adaptive bulk chunking, and
retained payload is never re-chunked during recovery.

Lanes carry a failure-domain identity. Multiple sockets through one router or tunnel
pool may add capacity, but they are not counted as independent router paths. Tor circuit
isolation, separate Tor instances, separate SAM endpoints, separate destinations, and
separate I2P routers are represented explicitly rather than inferred from socket count.

## Protocol requirements

The protocol must provide:

- explicit versioned binary framing with bounded lengths and no Rust-specific encoding;
- session and stream identifiers plus byte offsets for ordered delivery;
- authenticated lane attachment and replay-resistant session epochs;
- connection- and stream-level flow control;
- acknowledgement ranges and retransmission over a different lane;
- bounded reorder and unacknowledged-data memory;
- dynamic lane addition, draining, failure, and recovery;
- bidirectional scheduling with independent telemetry;
- end-to-end confidentiality for applications that do not already encrypt; and
- stable structured counters sufficient to explain scheduler decisions without
  accumulating unbounded logs.

Cryptographic primitives and handshakes must use reviewed constructions. Custom means
that AnonSSH owns its multipath semantics and wire protocol, not that it invents
cryptographic algorithms.

## Proof obligations

The bond is not complete merely because frames compile or two sockets are open. It must
prove exact ordered delivery under asymmetric latency and capacity, simultaneous use of
eligible lanes, bounded memory, protected real-time scheduling during bulk load,
cross-lane recovery after failure, and useful aggregate goodput. Controlled two-lane
tests must deliver at least 80 percent of the lanes' independently measured aggregate
capacity after warmup, and adaptive chunking must retain at least 90 percent of a fixed
32 KiB comparison on the same paced paths. Live tests must cover multiple I2P routers
and Tor plus I2P, with hash-verified payloads and lane-level usage artifacts.
Fixed-cardinality evidence must sample 1, 2, 4, and 8 lanes per provider in both
directions, including simultaneous bidirectional load, and must derive protected and
bulk-eligible paths from runtime state rather than topology arithmetic.

The shipped executable retains its embedded test facility. Deterministic protocol and
fault tests are product tests, not a separate simulation or evidence product.

## Consequences

The SSH proxy is an adapter around the bond, and router management is a supervised
provider pool rather than a single route choice. Direct transport behavior remains a
fallback and regression oracle. Named TCP forwarding and dynamic endpoint advertisement
remain outside the default SSH path but are shipped only after their own bounded
authorization and cleanup obligations are specified and tested. Broader proxying and
Unix-socket forwarding remain deferred.
