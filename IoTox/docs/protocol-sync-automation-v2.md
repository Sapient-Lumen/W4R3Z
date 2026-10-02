# Sync automation policy v2

Status: frozen local durable format. Implemented in IoTox 0.45.0. This record does not cross the Tox
wire and changes no negotiated feature bit or peer frame.

## Purpose and bounds

One record binds an IoTox namespace to its owner-selected unattended action. Format v2 replaces the
single remote-principal slot in v1 with a canonical fixed-capacity principal array. The product
admits at most 15 remote sources: together with the local stable device this equals tree-v2's frozen
16-writer inventory limit. The sixteenth physical array slot is reserved and remains zero under the
current semantic bound.

Every record is exactly 4,808 bytes. Integers are unsigned big-endian. Unused fixed-width bytes and
every named reserved byte are zero. The file is one owner-owned, mode-0600, single-link regular file
inside the owner-owned mode-0700 automation directory; symlinks and any other size are refused.

## Canonical record

| Bytes | Size | Meaning |
|---:|---:|---|
| 0..7 | 8 | ASCII `IOTXSAU2` |
| 8 | 1 | format `2` |
| 9 | 1 | automation mode |
| 10 | 1 | activation mode |
| 11 | 1 | namespace byte length, 1..64 |
| 12..13 | 2 | source-path byte length, 0..4096 |
| 14 | 1 | remote-principal count, 0..15 |
| 15 | 1 | reserved zero |
| 16..23 | 8 | policy generation, nonzero |
| 24..27 | 4 | periodic interval milliseconds |
| 28..31 | 4 | initial retry milliseconds |
| 32..35 | 4 | maximum retry milliseconds |
| 36..39 | 4 | reserved zero |
| 40..71 | 32 | local stable-device Ed25519 signing public key |
| 72..135 | 64 | namespace bytes followed by zero padding |
| 136..647 | 512 | sixteen 32-byte remote-principal slots followed by zero slots |
| 648..4743 | 4096 | canonical absolute source path followed by zero padding |
| 4744..4807 | 64 | detached Ed25519 signature |

Automation modes are `1=disabled`, `2=publish`, `3=follow`, `4=writable`, and
`5=bidirectional`. Activation modes are `1=pull-only` and `2=verified`.

The principal vector is lexicographically sorted, contains no duplicates, and contains no all-zero
principal. Modes further constrain the fields:

- `disabled`, `publish`, and `writable` have zero remote principals;
- `follow` has exactly one remote principal and no source path;
- `bidirectional` has 1..15 remote principals and one canonical absolute source path.

The signature is Ed25519 over the IoTox domain-separated digest of bytes 0..4743 using domain
`iotox-sync-automation-policy-signature-v2`. Decoding re-encodes and requires byte equality, so an
alternative ordering, padding, or representation is invalid even if a signature primitive would
otherwise accept its semantic fields.

## v1 compatibility and migration

The reader continues to accept the exact 4,328-byte `IOTXSAU1` format and its original
`iotox-sync-automation-policy-signature-v1` domain. A v1 record maps its zero/one principal slot into
the vector model. An exact `put` remains a duplicate and does not rewrite or advance generation.
The first explicit policy mutation writes v2 and increments generation once.

Software that predates this decision does not understand v2. Upgrade every process that may read a
shared policy directory before adding a second remote writer; there is no silent downgrade and no
mixed-writer v1 representation.

## Multi-peer scheduling

At most one periodic action is in flight per namespace because publication, graph acceptance, and
writable projection share state. For a bidirectional policy, the scheduler scans the canonical
principal vector from a retained round-robin cursor and selects the first due source. Every source
has an independent next-attempt time and consecutive-failure count. Success schedules that source at
the ordinary interval; failure applies bounded exponential retry only to that source. Aggregate
content-free counters and the earliest next due time remain the public runtime projection.

An already active pull with no unanswered control frame is a successful `pending` observation: its
immutable file receive is still in flight and periodic automation remains on the ordinary interval.
It is not a failure and cannot increase exponential backoff. This rule applies equally to legacy
treepack/range, content-v2, and tree-v2 automation; only a genuine control, authority, session,
transport, or verification refusal advances the failure clock.

A claimed action carries the exact policy generation and selected stable principal. Replacement or
disablement makes an old completion stale and effect-free. A completion naming a principal outside
the exact signed policy is refused without releasing the claimed lane.

## Runtime source-change wakeups

ADR 0341 adds a runtime-only wake path above this frozen record. A Linux Agent may watch local source
trees with bounded recursive `inotify` watches and call `trigger_source_change` when it observes a
write, create, delete, move, or metadata event. That call accelerates the existing periodic lane; it
does not persist any new field in the 4,808-byte record.

For `publish` and `writable`, the next local publish/reconcile attempt is scheduled through the same
local-source pending clock. For `bidirectional`, source changes enqueue a local `publish` action
while remote-source pulls keep their round-robin per-principal schedule. This is how local edits
become visible without pretending that a peer pull published them.

ADR 0342 adds the default Agent debounce above that runtime wake path. Native Linux source-watch
events are coalesced for 250 ms before the local publish/reconcile lane becomes due. Coalescing is
non-sliding: a burst keeps the earliest pending due time instead of repeatedly delaying publication.
A source change observed while a publish is already active remains pending after that publish's
completion.

ADR 0353 adds a tree-v2-only busy republish cooldown at the Agent source-watch call site. If a
tree-v2 source change is observed while a publish is active, the preserved pending source publish is
clamped to at least 5 seconds after that active publish completes. For `publish` and `writable`
policies, that delayed pending source publish also suppresses an earlier ordinary periodic local
publish; for `bidirectional`, remote-source pulls remain independently due while the local source
republish cools down. This is still runtime state only and does not change the 4,808-byte signed
automation record.

ADR 0344 adds the first source-scan cost reduction behind that same lane. The Agent keeps one
in-process, per-namespace tree-v2 source digest cache. A selected regular file reuses its previous
digest only when the namespace, source path, projection policy, path, device, inode, mode, link
count, owner, size, mtime, and ctime all match a prior verified scan entry. Restart, projection
exchange, source/path/policy changes, or metadata mismatch fall back to hashing. This is not a
durable record and never replaces the periodic full tree walk.

The wake path is best-effort. Unsupported platforms, watch exhaustion, dropped events, deleted source
roots, and over-triggered directory events all fall back to the signed interval/retry schedule.
`sync-automation` may report `source-publish-pending=1` for any local-source wake that has not yet
completed.

## Sharing transaction

`sync-share NAMESPACE FRIEND read-write` resolves the current application-ready friend to its
transcript-bound stable principal. Prepare and commit both preflight the 16-writer wire limit and the
15-remote automation limit. Commit verifies any RecallRoot-signed authority record, then adds writer
and subscriber membership and stores the additive canonical automation policy. Exact repeats are
idempotent. Membership, authority, and automation remain separate durable checks; a retry completes
a safe partially durable authority or namespace update rather than treating it as success.

For three writers, each owner shares to the other two. That gives three friendship edges, six
directional owner grants, and two remote principals in each local automation record. No node gains
authority transitively merely because another writer trusts it.
