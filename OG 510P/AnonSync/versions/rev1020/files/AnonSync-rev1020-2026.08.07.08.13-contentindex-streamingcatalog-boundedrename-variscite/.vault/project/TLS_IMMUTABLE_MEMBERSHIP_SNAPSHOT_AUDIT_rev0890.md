# Immutable TLS membership snapshot authority audit — rev0890

## Mission connection

AnonSync's transport is not allowed to turn a cryptographically valid peer into
an authorized replica by implication. TLS establishes a protected session and
provides peer-authentication evidence under the configured trust policy. The
application still owns the narrower decision that one exact peer key is allowed
to act as one exact AnonSync actor epoch in one exact folder.

That distinction is central to the project:

> authentication evidence is an input to authority; it is not authority by
> itself.

Rev0889 introduced the first accepted-session owner, but represented the final
SPKI-to-actor decision as a caller-supplied `std::function`. Rev0890 replaces
that live callback with a validated immutable value. The change is small in
surface area and large in authority impact: after the TLS handshake completes,
no arbitrary AnonSync membership code runs while the accepted child, `SSL`
object, and pre-request authorization frontier are live.

OpenSSL callbacks configured on `SSL_CTX` can still run as part of the caller-
owned TLS trust stack during handshake. Rev0890 does not claim otherwise. It
removes the separate application membership callback that rev0889 invoked *after*
cryptographic peer authentication and immediately before constructing durable
application authority.

## The rev0889 defect

The sealed rev0889 path performed this sequence:

1. atomically accept and own a nonblocking, close-on-exec child;
2. create an `SSL` object and complete mutual TLS;
3. re-prove accepted-socket lifetime and mutable descriptor policy;
4. derive the peer certificate's exact lowercase SHA-256 SPKI digest;
5. invoke an arbitrary caller-owned membership resolver;
6. copy its returned `SyncReplicaActor`; and
7. construct an authenticated channel and receiver session.

The callback was documented as synchronous and required stable backing state,
but those requirements were not owned or mechanically enforced by the accepted-
session object. More importantly, the callback itself was arbitrary in-process
code at the narrowest authority frontier. It could:

- mutate process-visible descriptor or TLS configuration state;
- re-enter file-delivery or durable-owner APIs;
- block indefinitely while the accepted child and `SSL` lifetime remained held;
- throw after nonlocal side effects;
- race a mutable membership map despite the comment-level contract; or
- accidentally couple authorization to unrelated locks, allocation, logging,
  network, or configuration activity.

The rev0889 source proceeded directly from callback return to authenticated-
channel construction. It did not compare the accepted socket lifetime and
policy across that callback. Adding only a post-callback reproof would have
caught some observable descriptor contradictions, but it would not undo
reentrant durable effects, lock inversion, unbounded blocking, mutation of other
service state, or a membership decision made from a racing map. Reproof is not
purity.

The correction is therefore architectural: remove the callback from this
frontier.

## New immutable authority value

`SyncReplicaTlsMembershipSnapshot` owns one complete authorization set for:

- one exact `folder_id`;
- one exact local `SyncReplicaActor`;
- one positive caller-owned `policy_epoch`; and
- zero or more exact lowercase SHA-256 SPKI-to-actor mappings.

Construction performs complete validation before publishing shared state:

- folder and actor identifiers must be canonical portable sync IDs;
- actor epochs and `policy_epoch` must be positive;
- membership count is capped at 65,536 entries before per-entry processing;
- every SPKI must be exactly canonical lowercase SHA-256 hex;
- the receiver's own `device_id` cannot be authorized as a peer;
- entries are sorted by SPKI;
- duplicate SPKIs are rejected, even if their actor values happen to match; and
- the complete canonical set is bound to a versioned SHA-256 digest.

Multiple distinct SPKI pins may map to the same actor. This deliberately permits
a bounded key-rotation overlap. One SPKI can map to only one actor, preventing
ambiguous authorization.

The state is private and retained as `std::shared_ptr<const State>`. The public
wrapper has no mutation API. Copies retain the same const state; moves
invalidate the source wrapper. The server takes the wrapper by value, so its
session scope has an independent lifetime handle without borrowing a mutable map
or callback from the caller.

This is C++ object-level immutability, not a claim that hostile code in the same
address space cannot corrupt memory. AnonSync does not treat mutually hostile
components within one process as a security boundary.

## Canonical digest

The snapshot digest uses the domain:

```text
anonsync:sync-replica-tls-membership-snapshot:v1
```

Every variable-length field is prefixed by one big-endian unsigned 64-bit
length. Counts and epochs are encoded as big-endian unsigned 64-bit values. The
digest binds, in order:

1. the versioned domain;
2. folder ID;
3. local device ID and actor epoch;
4. policy epoch;
5. canonical entry count; and
6. each sorted SPKI, peer device ID, and peer actor epoch.

Caller insertion order therefore cannot alter the digest. Folder, receiver,
policy epoch, pin, actor, and count changes do alter it. The digest is retained
in every `SyncReplicaFileTlsServerResult`, together with policy epoch and entry
count, including accept timeout and preauthentication terminal results.

This digest is structural evidence and an operator/debugging anchor. It is not a
signature, certificate, authorization token, freshness proof, or rollback
barrier. A malicious or stale configuration source can still construct a valid
snapshot for an obsolete policy epoch. The future durable membership owner must
provide anti-rollback and provenance separately.

## Accepted-session ordering

The server now executes this authority order:

1. validate the session label and `SSL_CTX` pointer;
2. prove that the snapshot's folder and local actor exactly match the selected
   file-delivery service;
3. copy snapshot epoch/count/digest into the result;
4. spend listener authority and accept one child;
5. complete the bounded mutual-TLS handshake;
6. re-prove accepted-socket lifetime, `O_NONBLOCK`, and `FD_CLOEXEC`;
7. derive the exact peer SPKI;
8. perform a pure binary search in the immutable snapshot;
9. reject an unknown pin before constructing application authority;
10. re-prove the same accepted socket and mutable policy after lookup; and
11. construct the authenticated channel and one-run receiver session.

The pre-accept service-identity check prevents a snapshot for another folder or
receiver actor from consuming even listener authority. Compiled tests make both
mismatches, then use the same listener with the correct snapshot and reach the
normal accept timeout. This proves that configuration mismatch is a pre-accept
cutpoint rather than an accepted-child failure.

The post-membership socket reproof is retained even though lookup is now pure.
It makes the boundary explicit and protects future maintenance from silently
inserting mutable work between authorization and channel construction.

## Failure and evidence matrix

| Condition | Accepted child | TLS complete | Peer authorized | Durable service | Result membership evidence |
|---|---:|---:|---:|---:|---:|
| snapshot/service mismatch | no | no | no | no | exception before result |
| accept deadline | no | no | no | no | exact snapshot bound |
| silent or malformed handshake | yes | no | no | no | exact snapshot bound |
| valid certificate, unknown SPKI | yes | yes | no | no | exact empty/nonmatching snapshot bound |
| mapped SPKI | yes | yes | yes | one bounded conversation | exact snapshot bound |
| durable effect, receipt timeout | yes | yes | yes | effect retained | exact snapshot bound |
| complete receipt | yes | yes | yes | effect retained; sender may settle | exact snapshot bound |

Unknown membership is not represented as handshake failure. A certificate can be
cryptographically valid under the TLS trust policy and still be unauthorized by
AnonSync. `PeerUnauthorized` preserves that distinction.

## Compiled coverage

The focused real-TLS executable now checks:

- canonical digest independence from caller entry order;
- exact lookup and unknown-pin rejection;
- multiple pins mapping to one actor during rotation overlap;
- policy epoch participation in the digest;
- moved-from snapshot invalidation;
- zero policy epoch rejection;
- entry-count hard-ceiling rejection;
- noncanonical SPKI rejection;
- duplicate SPKI rejection;
- local-device reflection rejection;
- malformed lookup rejection;
- folder and local-actor scope mismatch;
- pre-accept mismatch with unchanged durable state and reusable listener;
- accept timeout carrying exact snapshot evidence;
- valid-certificate/unknown-member rejection carrying the empty snapshot;
- complete TCP/TLS/request/publication/receipt/settlement carrying the exact
  authorizing snapshot; and
- unchanged canonical evidence convergence at the receiver and sender.

The lexical audits explicitly disclaim semantic proof. Their purpose is to make
removal of the snapshot source, reintroduction of the callback type, loss of
pre-accept scope binding, or reordering of the reviewed frontier visible in
ordinary CTest.

## Standards and implementation research

The design follows a separation already present in the standards ecosystem:

- OpenSSL 3.5 documents that in server mode `SSL_VERIFY_PEER` requests and checks
  a client certificate, while `SSL_VERIFY_FAIL_IF_NO_PEER_CERT` makes absence
  fatal. That is TLS certificate verification policy, not AnonSync actor
  authorization.
- OpenSSL separately documents that merely obtaining a peer certificate does
  not indicate its verification state; the application must inspect the
  verification result. Rev0889/0890 already do peer-profile validation before
  deriving the SPKI.
- RFC 5280 states that a certification path valid under the baseline algorithm
  may still be inappropriate for a particular application and permits the
  application to further limit valid paths. AnonSync's exact SPKI membership is
  an application authorization restriction layered after TLS validation.
- RFC 9001 states that peer-authentication requirements depend on the application
  protocol and deployment, and that client-authentication requirements vary by
  application. This supports keeping replica membership in AnonSync rather than
  treating generic CA validity as replica enrollment.
- RFC 9525 further separates service-identity matching from certification-path
  validity. It is primarily about server service identity, not AnonSync's
  client-device membership, but reinforces the broader lesson that certificate
  processing has distinct layers.

Primary sources reviewed on 2026-07-23:

- https://docs.openssl.org/3.5/man3/SSL_CTX_set_verify/
- https://docs.openssl.org/3.5/man3/SSL_get_peer_certificate/
- https://www.rfc-editor.org/info/rfc5280
- https://www.rfc-editor.org/info/rfc9001
- https://www.rfc-editor.org/info/rfc9525

## Rejected alternatives

### Keep the callback and re-prove afterward

Rejected. This catches only observable capability mutation. It cannot erase
reentrant side effects, bound execution, prevent lock inversion, or make a
racing backing map immutable.

### Hold a mutex around a mutable membership map

Rejected for the live accepted-session seam. It imports lock lifetime and
potential blocking into authentication, does not produce a stable policy digest,
and makes every session depend on mutable global ownership. A configuration
owner may use locks while *building* the next snapshot, then publish the frozen
value.

### Put actor identity in a certificate subject field

Rejected as the only authorization source. Certificate naming and path validity
are not the complete AnonSync enrollment policy, and a generic trusted CA must
not automatically authorize every certificate it can validate. Exact key pins
also keep the current implementation's actor mapping explicit.

### Make `policy_epoch` imply freshness

Rejected. A number supplied by the same untrusted or rollback-prone source as the
entries cannot prove that it is current. Freshness needs durable monotonic state,
provenance, and a defined recovery model.

### Copy the full map into every accepted session

Rejected. Canonical construction already freezes the set. A const shared state
keeps per-session copy cost bounded while preserving exact lifetime and avoiding
a new mutable global dependency.

## Remaining work and speculation

The next production membership owner should likely be a durable, versioned
configuration state machine rather than a mutable daemon map. One plausible
shape is:

1. validate a signed or otherwise authenticated membership update;
2. bind folder, local actor, prior policy digest, new monotonic generation,
   complete entry set, and administrative reason;
3. commit it under one SQLite writer transaction;
4. reconstruct and attest the complete current set on restart;
5. publish a new immutable snapshot only after durable commit; and
6. retain old snapshot generations long enough to explain in-flight session
   authorization and rejected stale configuration.

That is a design direction, not an implemented claim. The project still needs
explicit enrollment, revocation, key-compromise response, rotation overlap
expiry, device recovery, administrator identity, signed update provenance,
offline-device policy, and rollback handling.

SPKI pinning also creates stable linkability. Even with payload confidentiality,
a long-lived key and recurring network endpoint are observable identifiers. Key
rotation and relays may reduce some linkability but do not create anonymity.
AnonSync should continue to avoid claiming privacy properties that its membership
and transport metadata do not deliver.

## Nonclaims

Rev0890 does not provide a durable membership database, signed enrollment,
certificate revocation, actor-key recovery, policy freshness, rollback
protection, global concurrent-session limits, hostile same-process isolation,
anonymity, unlinkability, or externally trusted build provenance.

It proves a narrower property in this cloudtainer: one complete canonical
SPKI-to-actor set can be validated and frozen before accept, retained by value
through a one-shot TLS session, used without an arbitrary post-handshake
membership callback, attributed in every terminal result, and composed with the
existing durable receiver and exact receipt path.
