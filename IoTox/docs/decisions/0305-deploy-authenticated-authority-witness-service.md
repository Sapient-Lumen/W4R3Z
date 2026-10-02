# ADR 0305: Deploy an authenticated authority witness service

- Status: accepted and implemented for the authority lane; independent deployment qualification remains operator-owned
- Date: 2026-09-02

## Context

ADR 0303 implemented the authority transaction coordinator but deliberately stopped at an injected
backend contract. Its in-memory exact-CAS implementation shares the Agent process and failure domain,
reports `independently_controlled=0`, and is rejected in production. That proved crash ordering but
could not detect restoration of the Agent's complete local disk in a deployment.

The first network backend must not turn a TCP endpoint, bearer token, or configuration boolean into
an independence claim. It must authenticate both sides, preserve exact pending/committed CAS
semantics across lost replies, require explicit enrollment, and fail before the Agent exposes any
runtime or network surface when freshness cannot be reconciled.

## Decision

Add a separately runnable witness role to the ordinary `iotox` binary. It uses a dedicated
Ed25519 witness identity which cannot be loaded as a device or release-signer identity. The Agent
pins that public key. Every fixed-size request is signed by the stable device identity and binds a
fresh nonce, domain, device, witness epoch, closed lane, and exact expected/desired records. Every
response binds the request nonce and is signed by the dedicated witness identity. Network transport
does not carry an unlock secret or bearer credential; confidentiality is not required for these
public selectors and digests, while authentication and replay resistance are mandatory.

Enrollment is explicit, device-signed, and no-replace. A quiescent device emits one artifact binding
its exact committed authority head to a create-once random domain and nonzero witness epoch. The
service verifies the device signature and creates exactly one owner-private record. Normal network
traffic cannot enroll, reset, decrement, or change a selector. The service accepts only the two
canonical transitions from ADR 0303: committed to one-step pending, and that exact pending to
committed.

The service store signs every durable record with its witness identity, uses crash-atomic replace and
parent synchronization, rejects weak metadata/tampering, and takes an exclusive process lock. The
TCP listener uses bounded fixed records and timeouts. Truncated connections, port probes, resets,
timeouts, and lost response delivery consume only that client connection; they cannot terminate the
daemon. A valid request that exposes a durable or cryptographic store failure remains fatal rather
than silently serving uncertain state.

The Agent selects the backend only when host, port, pinned witness key, domain, and epoch are all
present. The authority intent path is explicit or derives beside the ledger. `run-check` validates
the closed selection without contacting the service. Live startup constructs the authenticated
backend after loading the device identity, then performs authority reconciliation before creating
`RuntimeTree`. Service absence, wrong key, missing enrollment, stale local state, fork, or an
unresolved pending transition fails closed.

The operator ceremony is intentionally split across the two control domains:

1. create the witness identity and private store on the witness host;
2. stop/quiesce the Agent and generate a random domain;
3. create a device-signed enrollment for the exact authority head;
4. transfer the non-secret signed enrollment artifact to the witness administrator and enroll once;
5. return and pin the witness public key, domain, and epoch in the Agent's protected configuration;
6. start the witness service, then start the Agent.

## Consequences

IoTox now has a production-capable authenticated remote backend for its authority freshness
coordinator. Eight new owned checks bring the direct registry to 767. They cover fixed protocol
records, enrollment binding/tamper refusal, persistent begin/commit, two-client CAS election, a wrong
pinned signer, durable record tampering, exclusive service ownership, real authority commit/restart,
and survival of a truncated accepted connection.

The retained two-guest NixOS gate runs the source-linked release binary on separate Agent and witness
VM disks/processes. It enrolls position zero, commits RecallRoot bootstrap to position one, deletes
the complete valid local ledger/guard pair, and proves refusal before runtime creation while the
witness remains advanced. It then proves exact-current restoration, service-outage refusal, service
restart, wrong-pinned-key refusal, and final recovery.

The implementation does not prove that an arbitrary deployment is independent or monotonic. The
two guests share one physical host and administrator. A service placed on the Agent host or backed by
the same snapshots is not an independent witness, and restoration of the service's own complete disk
state is outside its self-signature. Production deployment must use a separately administered
storage/failure domain with rollback-resistant or independently checkpointed persistence. TCP also
does not guarantee availability or confidentiality. Witness replacement/re-anchor, higher epochs,
broader lanes, and exhaustive crash/restore campaigns remain workstream 8 gates.
