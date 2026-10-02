# IoTox signed synchronization HEAD v1

**Implemented:** local publication and default-off remote synchronization primitive

**Wire allocation:** carried inside the negotiated state-sync-v1 HEAD result

**Signer:** stable IoTox device identity

**Encoded size:** 296 bytes

The signed synchronization HEAD is the sole mutable publication pointer for one writer's immutable
namespace revisions. It replaces the preserved toxsync component's separate HEAD key with the stable
IoTox device signing identity already named by namespace policy and authority proof.

## 1. Fixed record

All integers are unsigned big-endian. Unused bytes are zero.

| Offset | Size | Meaning |
|---:|---:|---|
| 0 | 8 | ASCII `IOTXSHD1` |
| 8 | 1 | engine: `1` range-v1, `2` content-v2, `3` treepack-v1 |
| 9 | 1 | namespace byte length, `1..64` |
| 10 | 6 | zero |
| 16 | 8 | generation, nonzero |
| 24 | 8 | artifact bytes, nonzero |
| 32 | 8 | manifest bytes, nonzero |
| 40 | 32 | stable writer signing public key |
| 72 | 32 | parent signed-record digest; zero only for genesis |
| 104 | 32 | immutable artifact digest |
| 136 | 32 | immutable manifest digest |
| 168 | 64 | namespace bytes followed by zero padding |
| 232 | 64 | Ed25519 signature |

The first 232 bytes are the signing body. Decoding requires the exact total size, magic, engine,
namespace grammar and length, zero reserved bytes, zero namespace padding, and canonical re-encoding.
Semantic verification additionally requires the namespace policy, writer membership, matching engine,
nonzero identities/sizes, and configured artifact/manifest bounds.

## 2. Signature and record identity

IoTox first computes its fixed BLAKE2b-256 domain hash over the signing body:

```text
S = IoToxHash("iotox-sync-head-signature-v1", bytes[0..231])
```

The stable device identity signs `S` with Ed25519. Verification uses the writer key embedded in the
record and requires that exact key in the local namespace writer set.

The linked record identity covers the complete signed 296-byte record:

```text
R = IoToxHash("iotox-sync-head-record-v1", bytes[0..295])
```

An accepted candidate receives `R` only after signature and policy verification. Callers do not
supply or guess the record digest.

## 3. Publisher transition

Genesis is generation 1 with a zero parent. A successor:

- is signed by the same stable writer as its immediate predecessor;
- increments generation by exactly one;
- sets parent to the predecessor's complete signed-record digest;
- uses the namespace's fixed engine; and
- names nonzero immutable artifact/manifest identities within local quotas.

The local creator derives generation, parent, writer, namespace, and engine rather than accepting
them from an operator request. A predecessor is signature-verified before use. Generation exhaustion,
a foreign predecessor signer, invalid policy, or out-of-bounds content fails before signing.

## 4. Durable publisher store

The current local publisher HEAD is stored at:

```text
NAMESPACE_ROOT/published-heads/<namespace>.signed-head
```

The configured store root must equal the namespace policy root. Loads use `O_NOFOLLOW`, require one
owner-owned, single-link, mode-0600 regular file of exactly 296 bytes, then decode and verify the
complete record. Corrupt, truncated, oversized, linked, permission-weakened, wrong-policy, or
wrong-signer state fails closed.

Publication serializes threads and separate local processes, constructs and verifies the successor,
computes its record identity before mutation, and atomically replaces the fixed state file last.
Cross-process exclusion uses one private persistent advisory lock per namespace. Retrying an exact
artifact/manifest/size tuple under the same writer returns the existing signed record as a duplicate;
it does not consume a generation.

## 5. Retained nonclaims

- This record alone does not prove artifact or manifest bytes exist. The implemented publication and
  subscriber paths commit and reverify both immutable objects before publication/acceptance and keep
  activation separate.
- Engine 3 authenticates deterministic directory semantics; it does not authorize extraction,
  execution, arbitrary destination paths, range reconstruction, or path-level merging by itself.
- The local advisory lock is cooperative and local-filesystem scoped; it is not a distributed lease.
- Restoring an older valid signed HEAD and its surrounding local state together still requires an
  external monotonic witness or later guard to detect after restart.
- A valid signature does not grant `sync.publish`, namespace administration, subscription,
  activation, or firmware installation authority.
