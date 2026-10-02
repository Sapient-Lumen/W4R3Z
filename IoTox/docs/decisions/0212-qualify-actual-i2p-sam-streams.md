# ADR 0212: Qualify the actual-I2P SAM stream seam

Status: accepted bounded construction evidence, 2026-08-28.

## Context

ADR 0211 freezes an exact numeric SOCKS5-to-SAM v3.1 adapter and independently tests its framing,
mapping, loss, recovery, and audit behavior. A process double cannot establish that real I2P
tunnels, LeaseSet publication/discovery, or streaming transport work. Product `tox/i2p` must still
fail closed until the c-toxcore and application edges receive source-linked Sandwurm containment
evidence.

The smallest honest next gate is therefore below Tox: two distinct real router processes, an actual
published I2P Destination, the strict adapter, concurrent exact-byte streams, process/socket/source
attribution, and a content-free independently verifiable receipt.

## Decision

Add `tools/run-i2p-sam-smoke.py` and `tools/verify-i2p-sam-smoke.py`. The live runner:

- requires a clean IoTox commit, distinct router PIDs and loopback SAM endpoints, exact executable
  attribution, router-owned SAM listeners, and at least one public TCP peer per router;
- commits the router executable and complete immutable source tree, including contained relative
  symbolic links, without copying either into the repository;
- creates one transient Ed25519 server session with unencrypted LeaseSet2 and ECIES-X25519 keys on
  the first router, while the ADR 0211 adapter creates its outgoing transient session on the second;
- maps one documentation-only numeric Tox record to one exact traditional b32 Destination, retaining
  only the same domain-separated commitment on both the server and adapter sides;
- permits one bounded byte-verified warm-up so LeaseSet discovery is separated from measurement and
  records every pre-discovery denial rather than deleting it;
- barrier-releases four clients, each carrying a distinct deterministic 65,536-byte payload, and
  requires byte identity at the server and on echo;
- retains one pending server-side SAM accept at a time but dispatches established streams to
  concurrent workers; and
- writes one no-clobber, content-free receipt containing exact counters, canonical adapter audit
  records, payload/remote set commitments, process/socket commitments, and timings, but no b32 name,
  full or private Destination, payload, or public peer address.

The verifier rejects duplicate JSON members and unknown/missing fields. It reconstructs all payloads,
set commitments, and canonical audit bytes; enforces exact discovery-before-five-admissions ordering;
joins the shared b32 commitment; verifies distinct process and SAM identities; binds the adapter blob
at the historical source commit; and optionally rehashes the supplied router executable and source
tree. It does not claim to reobserve terminated processes or network traffic from a retained receipt.

## Router compatibility finding

The first live attempt issued four simultaneous `STREAM ACCEPT` commands to i2pd 2.60.0. Two streams
completed and two accept sockets closed before a complete status line. Source review located the
cause in both queued-accept expiry loops in `libi2pd_client/SAM.cpp`: the loop removes entries while
`queued_time + 3 seconds > now`, which selects fresh entries rather than expired ones. IoTox does not
patch or vendor i2pd here. The gate keeps one accept pending, immediately dispatches an accepted
stream, and then installs its successor. Client streams remain concurrent. This is an i2pd 2.60.0
compatibility rule, not a SAM protocol restriction.

A second construction attempt also showed that a newly published Destination may initially return
`denied-stream`. Warm-up discovery is therefore explicit and measured. The accepted run happened to
need one attempt and zero discovery denials; future runs may record bounded denials without relabeling
them as application-stream success.

## Qualification

Accepted receipt `artifacts/rev0045/i2p-sam-two-router-smoke.json` binds:

- clean IoTox commit `a1f3b53129ee15997a6f7f26be5d71d799aab837`;
- i2pd 2.60.0 / I2P 0.9.69, executable SHA-256
  `9d537e84fd9808a40435305b04ca3c05819b8f2cf005808b475777bafe87d500`;
- 315-entry router source-tree SHA-256
  `f06e0917255e5cd3b772ffe9722e141f8842bf262d448ccc437292e8e4f739f0`;
- two distinct router processes, SAM endpoint commitments, and 12/49 public TCP peer counts;
- 9.018-second server-session setup and one 4 KiB warm-up in 2.526 seconds;
- four client releases within 82,150 ns;
- four distinct 65,536-byte payloads, 262,144 measured bytes total, and one remote-Destination
  identity; and
- byte-identical completion at 23.689, 24.970, 25.390, and 24.722 seconds.

The retained receipt verifies both standalone and against the exact still-present Nix router inputs.
The default CTest graph runs the standalone verifier and the runner's offline self-test.

## Consequences

- Actual I2P STREAM transport through IoTox's strict construction adapter is now evidenced on one
  physical host and two distinct router processes.
- The latency values are construction observations dominated by fresh I2P path behavior. They are
  not an interactive-performance target, throughput result, availability statement, or SLA.
- Product `tox/i2p` remains unsupported. This gate carries no c-toxcore packet, Tox identity,
  friendship, private route binding, Ratox frame, sync object, guest TAP capture, reconnect fault, or
  anonymity evidence.
- The next gate remains an I2P-hosted Tox TCP bootstrap/relay service plus two source-linked
  Sandwurm guests, exact leak containment, route loss/recovery, private membership, and one exact
  Ratox or sync payload with raw/compact proof.

See `docs/i2p-route-construction.md` and
`docs/evidence/2026-08-28-actual-i2p-sam-streams.md`.
