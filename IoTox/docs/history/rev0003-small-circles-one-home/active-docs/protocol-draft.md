# IoTox protocol draft

This is a research protocol seed, not a frozen interoperability standard.

## Transport lanes

### Lossless control lane

IoTox currently uses Tox lossless custom packet identifier `0xA0`. The targeted toxcore
API caps a custom packet at 1,373 bytes. The fixed IoTox header is 41 bytes, leaving
1,332 bytes for one bounded control payload.

All integer fields are unsigned big-endian values.

| Offset | Size | Field |
|---:|---:|---|
| 0 | 1 | packet identifier `0xA0` |
| 1 | 1 | protocol major |
| 2 | 1 | protocol minor |
| 3 | 1 | message type |
| 4 | 1 | flags |
| 5 | 4 | payload length |
| 9 | 8 | message ID |
| 17 | 8 | correlation ID |
| 25 | 8 | sequence |
| 33 | 8 | expiry Unix time in milliseconds; zero means unspecified |
| 41 | N | payload |

The decoder rejects truncation, oversized packets, the wrong packet identifier, unknown
message types, and payload-length mismatches.

### Bulk lane

Large firmware, diagnostics, and immutable Mutorr objects should use Tox file transfer.
IoTox should not create a second arbitrary bulk-fragmentation protocol inside the
custom-packet lane.

A future transfer manager needs stable application transfer IDs, direction, Tox file
number, object/artifact digest, size, authorization decision, storage reservation,
restart behavior, cancellation, and integrity verification.

## Current message-type reservations

| Value | Name | Intended role |
|---:|---|---|
| 1 | `HELLO` | protocol and identity introduction |
| 2 | `CAPABILITIES` | feature/version negotiation |
| 3 | `COMMAND` | authorized requested operation |
| 4 | `COMMAND_RESULT` | operation progress or terminal result |
| 5 | `STATE_SNAPSHOT` | complete bounded state view |
| 6 | `STATE_EVENT` | incremental state change |
| 7 | `ACKNOWLEDGEMENT` | application-level acceptance/progress acknowledgement |
| 8 | `ERROR` | structured protocol/application error |
| 9 | `PAIR_REQUEST` | claim/pairing request |
| 10 | `PAIR_RESULT` | claim/pairing result |
| 11 | `REVOKE` | authorization or endpoint revocation |
| 12 | `OTA_MANIFEST` | signed update metadata |
| 13 | `MUTORR_HEAD` | announce one linked mutable head |
| 14 | `MUTORR_INVENTORY` | summarize known heads or immutable objects |
| 15 | `MUTORR_WANT` | request missing history or objects |
| 16 | `MUTORR_OBJECT_OFFER` | advertise object availability/transfer metadata |

These values are validated by rev0003 code but remain provisional. The protocol major
is parsed but no full version-negotiation state machine exists yet.

## Common application requirements

Future payloads should include or bind, as appropriate:

- target stable device identity;
- sender application identity;
- ownership epoch;
- authorization-ledger revision or grant identity;
- request/message ID;
- correlation ID;
- issued-at time and/or relative TTL;
- idempotency policy;
- signature or message-authentication evidence;
- protocol feature requirements;
- bounded payload schema version.

Tox authenticates and encrypts the transport session. High-consequence IoTox operations
should still carry independent application authorization so a transport defect does not
automatically become actuator authority.

## Version negotiation

A peer connection should begin with `HELLO` and `CAPABILITIES`.

The eventual negotiation rules should distinguish:

```text
protocol major: incompatible framing or semantic break
protocol minor: additive compatible evolution
required feature: operation cannot proceed without it
optional feature: may be ignored
implementation version: diagnostic only, not capability proof
```

Unknown optional fields should be ignored within strict bounds. Unknown required
features should produce an explicit incompatibility result.

## Command and result semantics

Transport delivery is not execution. A hardware-affecting command may move through:

```text
RECEIVED   durably accepted and authorized for later evaluation
STARTED    execution began
SUCCEEDED  operation completed
FAILED     terminal failure
EXPIRED    deadline passed before safe execution
REJECTED   authorization, validation, or policy denied it
```

A retry with the same stable command ID should return the recorded prior result rather
than repeating an operation unless the command is explicitly non-idempotent and the
caller accepts that risk.

The current code does not implement these durable semantics yet.

## RecallRoot re-entry protocol

RecallRoot-v1 is implemented as a local root derivation contract, but no over-Tox
re-entry transcript is frozen.

A future protocol must ensure:

- the phrase and RecallRoot never cross the network;
- owner application keys are domain-separated from Tox endpoint material;
- challenges are fresh and bound to a specific device and ownership epoch;
- replay cannot authorize a new controller;
- devices can recognize a reconstructed owner without a vendor lookup;
- phrase compromise and owner-root transition have explicit race behavior;
- ordinary daily messages use delegated keys rather than the high-value root.

Potential pairing/re-entry message types may be added later rather than overloading the
current provisional `PAIR_REQUEST` payload prematurely.

## Authorization records

The authorization ledger needs canonical signable records for:

```text
owner root
controller delegation
role/capability grant
namespace membership
temporary access
revocation
ownership epoch transition
route endpoint binding
```

Record encodings, signing primitive, hash, and rollback strategy are not selected in
rev0003.

## Mutorr mutable-head payload

`MUTORR_HEAD` currently carries one fixed 221-byte record.

| Offset | Size | Field |
|---:|---:|---|
| 0 | 1 | head wire version, currently `1` |
| 1 | 32 | namespace ID |
| 33 | 32 | writer signing key |
| 65 | 8 | generation, starting at `1` |
| 73 | 32 | current immutable root digest |
| 105 | 32 | previous link; currently previous root |
| 137 | 8 | creation Unix time in milliseconds |
| 145 | 8 | declared content bytes |
| 153 | 4 | declared object count |
| 157 | 64 | opaque signature |

Bytes `0..156` are the canonical signing body. Signature algorithm, key storage, and
verification are intentionally absent.

Validation rules implemented in rev0003:

- supported head wire version;
- non-zero namespace, writer, and root;
- generation at least one;
- generation one has a zero previous link;
- later generations have a non-zero previous link;
- exact payload size.

After external authorization and signature verification, the evaluator classifies:

```text
no current + generation 1     -> accept initial
no current + later generation -> request history
same complete record          -> duplicate
earlier generation            -> stale
same generation, different    -> conflict
later + previous=current root -> accept advance
later + other previous        -> request history
other namespace or writer     -> different stream
```

The previous-link meaning is not frozen. Binding the complete previous head rather than
only its root may better preserve signed metadata and equivocation evidence.

## Planned Mutorr gossip

1. An authorized writer creates immutable objects, computes a root, creates and signs a
   new head, and sends it to current Cube neighbors.
2. A receiver verifies membership epoch, writer capability, signature, bounds, expiry,
   and deduplication before considering progression.
3. A new valid head is forwarded to neighbors other than the sender within bounded hop,
   queue, and retry policy.
4. Missing history or objects produce a bounded `MUTORR_WANT`.
5. Peers return bounded inventories or offers.
6. Bulk object bytes use Tox file transfer and are accepted only after cryptographic
   integrity and authorization checks.
7. Periodic anti-entropy repairs sleeping or temporarily partitioned members.

## Membership epochs

A Cube is meaningful only relative to a specific authorized membership snapshot. Future
Mutorr messages should bind a namespace membership epoch or snapshot digest.

Open questions include:

- who may advance the epoch;
- how concurrent changes are resolved;
- whether an old member may serve old encrypted objects;
- how removed members lose future read capability;
- how peers reconcile when they missed several epochs;
- whether topology transitions overlap to avoid partitions.

## Object confidentiality and identity

The object format is not defined. Candidate design questions include:

- hash plaintext, ciphertext, or a canonical object envelope;
- deterministic versus randomized encryption and equality leakage;
- namespace key hierarchy and per-object subkeys;
- reader key envelopes;
- chunking and Merkle manifests;
- metadata minimization;
- compression before or after encryption;
- retention and cryptographic erasure;
- proof of possession versus simple availability claims.

A custodian role must not imply read authority.

## Clock and expiry caveats

Many IoT devices boot with incorrect wall clocks. Unix timestamps alone are not a safe
ordering or freshness mechanism.

The eventual protocol may need a combination of:

- relative TTL;
- sender epoch/boot nonce;
- monotonic counters;
- peer clock estimates;
- signed issued-at time with tolerance;
- replay windows independent of wall time.

Mutorr head generation and signed lineage, not `created_unix_ms`, determine stream
order.

## Required decoder limits

Every variable payload decoder must bound before allocation or iteration:

- total payload bytes;
- nesting depth;
- map/array/string lengths;
- inventory count;
- requested object count;
- transfer count;
- signature/key count;
- namespace/member count;
- decompressed size;
- per-message and per-peer computational work.

CBOR remains a likely payload encoding, but no implementation or canonical subset is
selected.
