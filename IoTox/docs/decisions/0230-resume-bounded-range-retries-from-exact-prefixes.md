# ADR 0230: Resume bounded range retries from exact prefixes

Status: accepted implementation, deterministic failure coverage, and genuine Sandwurm
qualification, 2026-08-29.

## Context

ADR 0138 made one same-job range retry safe by clearing the first attempt and allocating fresh
durable and transport identities. Its original implementation intentionally discarded every partial
byte. ADRs 0223 and 0224 subsequently established a stricter primitive: an upper protocol can own one
private attempt inode from byte zero, revalidate its exact prefix, hand it to a fresh fenced attempt,
and ask c-toxcore to seek before receiving only the suffix.

The first live qualification of range-prefix reuse exposed an important integration distinction.
The subscriber named its canonical attempt path, but an initial range still used the ordinary
publish-on-completion file receiver. Partial bytes therefore lived in a transport-private temporary
inode. The subscriber correctly found no exact attempt prefix and fell back to discarding the bytes.
Range retry can claim prefix reuse only when the first byte is written into the canonical private
attempt inode under the same strict contract used for continuation.

## Decision

- When the seek-capable receive seam exists, every range receive creates the exact owner-only,
  mode-0600, single-link attempt inode under the namespace transaction and admits it in place from
  offset zero. Offset zero sends no Tox seek because a new transfer already begins there. Platforms
  without that seam retain the fully-discarded ADR 0138 fallback.
- A receive-ceiling refusal before transport admission preserves the exact empty inode, signed active
  attempt, FileId, and pending offer. A later admission revalidates that the same path is still an
  empty strict partial before using it; it does not allocate a second attempt.
- An incomplete range is eligible for retention only while its single configured retry remains, its
  reported position is positive and strictly below the bundle size, its local path is the exact
  attempt path, and strict inspection reports exactly that many bytes. Any mismatch discards the
  attempt and increments `range-retention-fallbacks` rather than trusting the prefix.
- Before retry, the subscriber finishes and signs the old active-attempt truth and fences its
  scheduler reservation. It then atomically hands the exact partial to a fresh durable attempt path,
  begins a fresh signed attempt record, and emits the unchanged HEAD/range plan under a fresh message
  ID and nonzero FileId. The job, authority epoch, namespace, and authenticated carrier remain fixed.
- The replacement offer must match the fresh FileId and complete bundle size. The file manager opens
  the handed-off inode without following links, rechecks owner/mode/link count/size, seeks c-toxcore
  to the exact prefix length, and receives only the suffix in place.
- `sync-status` exposes saturating `range-retained-bytes`, `range-resumed-bytes`,
  `range-discarded-bytes`, and `range-retention-fallbacks`. Retained bytes are not basis reuse and do
  not reduce the final `range-fetched-bytes`, which continues to describe the complete verified
  bundle.
- Complete reconstruction, target SHA-256 verification, immutable commit, signed HEAD acceptance
  last, and explicit exact-token activation are unchanged. No range frame, feature bit, authority
  rule, or retry bound changes.

This decision supersedes ADR 0138 only where it required every failed range prefix to be discarded.
ADR 0138's one-retry bound, fresh identities, cleanup/fencing order, and fail-closed terminal rules
remain in force.

## Evidence

The owned subscriber test cuts a 1 MiB range bundle exactly in half, hands the private prefix from
the old attempt to a fresh attempt, injects one receive-ceiling refusal, and proves later admission
seeks to byte 524,288. It requires fresh FileIds, exact retained/resumed equality, zero discarded
bytes and fallbacks, full artifact equality, generation-2 HEAD acceptance, and separate activation.
It also proves the initial offset-zero in-place receive and reuse of an exact empty partial across an
admission deferral.

The genuine `sync-file-range-retry` pair gate passes from clean source revision
`93a8a20614a7d69b91180c233920f048bcbec77e` with binary SHA-256
`2d8dc95b6363458b8ecd69fcfc450624f75eaf0317d04e3c053f06850c05e089`:

| Route | Compact proof | Retained = resumed | Discarded | Fallbacks | Pair span |
|---|---|---:|---:|---:|---:|
| direct UDP | `pair.cj5y5vgt` | 15,081 bytes | 0 | 0 | 286,693,076,623 ns |
| forced TCP | `pair.qeb99i4o` | 24,678 bytes | 0 | 0 | 436,728,451,016 ns |

Each cell uses distinct first/replacement FileIds, fetches the complete 1,048,576-byte logical range
bundle with only its suffix retransmitted, reuses 3,145,728 verified basis bytes, reconstructs the
same 4,194,304-byte artifact, accepts generation 2 last, and explicitly activates it. Both raw roots
and both 155,648-byte secret-free compact exports independently pass the strict verifier.

## Consequences

A transient same-carrier range failure no longer retransmits its already received exact prefix. The
qualified byte savings are the observed prefix sizes above; they are not latency, throughput, or
availability promises.

This does not resume the same Tox handle or durable attempt, survive process/guest restart, retain a
prefix across authenticated carrier loss, move a range prefix across carriers, revive a cancelled
job, reuse bytes for an explicit fresh job, retry more than once, or weaken complete-object and HEAD
verification. ADR 0231 later qualifies one separate native available-policy cross-carrier range
case; it does not broaden this retry decision. In particular, ADR 0228's failed I2P range prefix
remains discarded.
