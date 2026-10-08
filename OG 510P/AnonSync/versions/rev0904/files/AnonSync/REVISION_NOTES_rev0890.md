# AnonSync revision notes — rev0890

## Revision theme

Rev0890 removes arbitrary application membership code from the live accepted-
TLS authorization frontier. The rev0889 server derived a verified peer SPKI and
then invoked a caller-owned `std::function` to decide its actor epoch. That seam
borrowed mutable backing state and allowed unbounded, reentrant code to execute
while one accepted descriptor and `SSL` object were live immediately before
application authority was minted.

The replacement is a validated, canonical, immutable
`SyncReplicaTlsMembershipSnapshot` retained by value through the one-shot
session. It binds one folder, local actor, positive policy epoch, complete sorted
SPKI-to-actor set, entry count, and versioned structural digest. Unknown pins are
rejected without a callback. Cross-folder or cross-actor configuration is
rejected before accept authority is spent. Every terminal server result carries
the exact snapshot epoch, count, and digest used.

The revision also audits every explicit `std::function` in production source,
keeps the payload callback behind its existing post-callback channel and exact-
claim fences, distinguishes selftest interposition from product APIs, and adds
ordinary CTest inventory guards. The new implementation source is compiled into
the existing TLS-server library rather than adding another target to the already
fragmented build graph.

## Parent

The exact parent handoff is:

`AnonSync-rev0889-2026.07.23.07.25-acceptedsession-deviceisolation-v3rollback-copyfrontier.zip`

The parent archive digest and exact parent-relative delta are recorded in
`REVISION_EVIDENCE/rev0890/LINEAGE.json` and `LINEAGE.md`.

## Production C++ changes

### Immutable TLS membership authority

Added:

- `src/sync_replica_tls_membership_snapshot.hpp`
- `src/sync_replica_tls_membership_snapshot.cpp`

`SyncReplicaTlsMembershipSnapshot` validates and retains:

- one canonical folder ID;
- one canonical local actor and positive actor epoch;
- one positive caller-owned policy epoch;
- at most 65,536 entries;
- exact lowercase SHA-256 SPKI pins;
- exact peer actors; and
- a versioned digest over the complete canonical set.

Entries are sorted by SPKI. Duplicate pins are rejected. Distinct pins may map
to the same actor to represent an explicit key-rotation overlap. A pin mapping
to the receiver's own `device_id` is rejected. The complete state is private and
retained as `std::shared_ptr<const State>`; copies share const state, and moved-
from wrappers are inactive.

The snapshot digest is domain separated and length framed. It binds folder,
local actor, policy epoch, entry count, and every sorted pin/actor pair. It is
structural evidence, not a signature or anti-rollback mechanism.

### Accepted-session API and ordering

Extended:

- `src/sync_replica_file_tls_server.hpp`
- `src/sync_replica_file_tls_server.cpp`

Removed:

- `SyncReplicaTlsPeerActorResolver`
- the `<functional>` dependency in the server header; and
- the post-handshake application membership callback.

The one-shot server now takes `SyncReplicaTlsMembershipSnapshot` by value. It
proves snapshot/service folder and local-actor identity before `accept4`, records
snapshot policy epoch/count/digest in the result, performs exact immutable lookup
after verified SPKI derivation, rejects unknown peers, re-proves accepted socket
lifetime and `O_NONBLOCK`/`FD_CLOEXEC` policy after lookup, and only then mints
the authenticated channel.

OpenSSL callbacks configured on the caller-owned `SSL_CTX` may still execute as
part of the handshake trust stack. Rev0890 removes the separate AnonSync
membership callback at the post-handshake authorization frontier; it does not
claim callback-free OpenSSL internals.

### Build-graph restraint

Extended:

- `CMakeLists.txt`

The membership implementation is a separate translation unit so changes do not
force recompilation of the 500-line accepted-session source. It is included in
the existing `anonsync_sync_replica_file_tls_server` library rather than adding
another static library and link action. This is a small corrective response to
the cube's existing target proliferation.

## Runtime coverage

Extended:

- `tests/sync_replica_tls_transport_test.cpp`

New compiled coverage includes:

- canonical membership digest independent of input order;
- exact SPKI lookup and unknown-pin rejection;
- two key pins mapping to one actor during rotation overlap;
- policy epoch participation in the digest;
- moved-from snapshot rejection;
- zero policy epoch and over-ceiling membership rejection;
- noncanonical SPKI rejection;
- duplicate SPKI rejection;
- receiver-device reflection rejection;
- malformed lookup rejection;
- folder and local-actor scope mismatch;
- pre-accept mismatch with unchanged SQLite/effect state;
- reuse of the same listener by the correct snapshot after mismatch;
- accept-timeout result binding to the exact snapshot;
- certificate-valid, membership-unknown rejection binding to the empty
  snapshot; and
- full TCP/mutual-TLS/file publication/receipt/sender settlement and canonical
  convergence binding to the exact authorizing snapshot.

## Audit and refactor work

Added:

- `tools/audit_sync_tls_membership_snapshot.py`
- `tools/audit_authority_callback_boundaries.py`
- `TLS_IMMUTABLE_MEMBERSHIP_SNAPSHOT_AUDIT_rev0890.md`
- `CALLBACK_AUTHORITY_BOUNDARY_AUDIT_rev0890.md`

Extended:

- `tools/audit_sync_file_tls_server.py`
- `tools/verify_release_package.py`

The server audit is advanced to format v4 and now requires pre-accept snapshot
scope binding, immutable lookup, post-membership socket reproof, result evidence,
and absence of the retired callback surface.

The callback audit records the exact `std::function` inventory. It distinguishes:

- the removed TLS membership callback;
- the retained payload-source callback, which completes before SQLite writer
  guard acquisition and is followed by channel and exact-claim re-attestation;
- a production-empty SQLite report hook exposed only through a selftest bridge;
- peer-ingress selftest assertion sinks; and
- the separately owned SQLite C authorizer callback.

Both audits explicitly disclaim semantic proof. Their role is to detect source-
shape and inventory drift while compiled tests, independent compilers,
sanitizers, stress, and package verification carry behavioral evidence.

## Research

Primary sources reviewed for this revision are recorded in
`TLS_IMMUTABLE_MEMBERSHIP_SNAPSHOT_AUDIT_rev0890.md` and
`REVISION_EVIDENCE/rev0890/RESEARCH.md`. They include OpenSSL 3.5 peer-
verification and peer-certificate documentation, RFC 5280 application-specific
certificate restrictions, RFC 9001's application-dependent peer-authentication
requirements, and RFC 9525's separation of service identity from certificate-
path validation.

## Validation

Final validation results are bound under:

- `REVISION_EVIDENCE/rev0890/validation/VALIDATION_SUMMARY.json`
- `REVISION_EVIDENCE/rev0890/AUDIT.md`
- `RELEASE_GATE.json`

The handoff archive is published only after the final staged directory and the
immutable ZIP independently pass the release package verifier.

## Remaining priority work

The next authority implementation should be a durable membership configuration
owner that validates provenance, persists a monotonic generation and prior-
digest chain, reconstructs the complete set on restart, defines revocation and
rotation overlap, and publishes immutable snapshots only after durable commit.
The current positive `policy_epoch` is deliberately not represented as rollback
protection.

The highest remaining callback debt is `SyncReplicaFilePayloadSource`. It is
carefully fenced but still arbitrary local code whose execution and temporary
resource use are unbounded while a durable outbox lease exists. A bounded
content-addressed payload handle or reader capability should replace it in the
production service path.

In parallel, the project still needs bounded concurrent accept/handshake/session
ownership, peer/folder admission, total disk accounting, fair staging,
reclamation, compaction/rejoin policy, and a production executable that makes
the newer causal SQLite/TLS path—not the legacy stack—the user-visible authority.

## Nonclaims

Rev0890 does not claim durable enrollment, signed membership updates,
revocation, key recovery, policy freshness, rollback protection, a production
daemon, internet deployment safety, hostile same-process isolation, fair
scheduling, staged-payload reclamation, exactly-once network delivery,
anonymity, unlinkability, traffic-analysis resistance, formal verification, or
externally trusted build provenance.

It proves a narrower executable slice in this cloudtainer: canonical membership
can be validated and frozen before accept, used by value without an arbitrary
post-handshake membership callback, scoped to the exact receiver service,
attributed in every terminal result, and composed with the existing one-shot
mutual-TLS, durable file-effect, exact receipt, and sender-settlement path.
