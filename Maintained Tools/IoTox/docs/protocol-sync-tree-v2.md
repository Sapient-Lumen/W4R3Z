# IoTox tree-v2 synchronization wire v1

Status: frozen construction protocol, checkpoint extension 2026-09-01.

**Allocation:** feature bit 30 (`state-sync-tree-v2`); checkpoint feature bit 31
(`state-sync-tree-checkpoint-v2`); IoTox lossless message types 32--35.
All integers below are unsigned big-endian unless stated otherwise. Every unused byte is zero and is
checked on decode. Requests have a nonzero message ID and zero correlation ID; results have both a
nonzero message ID and a nonzero request correlation ID. Flags, sequence, and expiry are zero.

## Inventory request — type 32, 72 payload bytes

```text
0       u8      version = 1
1       u8      namespace length, 1..64
2..7    zero
8..71   namespace bytes followed by zero padding
```

The namespace follows the ordinary canonical namespace grammar.

## Manifest identity

Canonical manifest bytes that fit the original bounded hash operation retain the exact
`iotox-sync-tree-v2-manifest-v1` BLAKE2b-256 identity. Larger valid manifests use the backward-safe
ADR 0280 extension: ordered 60 KiB leaves bind `u32 index`, `u32 leaf-count`, `u64 total-bytes`, and
the leaf bytes under `iotox-sync-tree-v2-manifest-chunk-v1`. An `IOTXTMH1` root binds `u32
leaf-count`, `u32 total-bytes`, and the ordered 32-byte leaves under
`iotox-sync-tree-v2-manifest-chunk-root-v1`. The manifest encoding and object wire kind do not
change. Namespace byte and object quotas remain authoritative before identity construction.

## Inventory result — type 33, 72 + 72 × writer-count payload bytes

```text
0       u8      version = 1
1       u8      status: available=1, absent=2, denied=3, unavailable=4
2       u8      namespace length
3       u8      writer count, 0..16
4..7    zero
8..71   namespace bytes followed by zero padding

For each writer, sorted strictly by the 32-byte stable writer key:
0..31   writer public key
32..39  branch generation, nonzero
40..71  SHA-256 identity of the complete signed branch record
```

`available` requires at least one record. Every other status requires zero records. Inventory is an
entry point, not authority to accept values: the subscriber must fetch and verify the complete
predecessor/observation closure named by each signed record.

If any advertised record's reachable closure contains branch format 2, the publisher and subscriber
must have negotiated feature bit 31 as well as bit 30. A publisher refuses that inventory—and a
direct checkpoint-object request—to a peer lacking bit 31; a subscriber independently refuses to
schedule the checkpoint. No new inventory or object message type is introduced.

## Object request — type 34, 144 payload bytes

```text
0       u8      version = 1
1       u8      kind: branch-record=1, manifest=2, file=3
2       u8      namespace length
3..7    zero
8..39   requested SHA-256 object identity
40..71  exact nonzero Tox FileId for the following offer
72..135 namespace bytes followed by zero padding
136..143 zero
```

Only one request lane is active in the first subscriber. A digest may be reused locally instead of
being requested, but a kind/digest pair cannot alias another kind in the graph scheduler.

## Object result — type 35, 88 payload bytes

```text
0       u8      version = 1
1       u8      status: offered=1, denied=2, absent=3, unavailable=4
2       u8      object kind
3..7    zero
8..39   exact requested object identity
40..71  exact requested FileId
72..79  object bytes
80..87  zero
```

A non-offered result has zero bytes. An offered branch record or manifest must be nonempty; an
offered file may be empty. The following Tox file offer must match the FileId, friend, online epoch,
declared bytes, and selected primary carrier exactly. Its completed staging file is independently
verified before commit.

## Ordering and authorization

The publisher evaluates `sync.subscribe` and namespace subscriber membership under the exact current
authority-v3 session. Its bounded FIFO exact-replay window binds request bytes and ID to friend,
online epoch, authority head, stable principal, and capabilities. An exact retained replay returns
the same control result without a second file effect; a conflicting retained replay is a protocol
error. Once retired, the identifier names fresh read-only work and must pass all current checks again
(ADR 0282).

The subscriber evaluates the peer's `sync.publish` and writer membership under the same exact
session. It commits file CAS first, then complete signed branch/manifest proofs in topological order,
then writer-current pointers, and finally the writable projection. A failed or offline job never
advances a partially proven branch.

Object scheduling is local and bounded. ADR 0329 permits a subscriber to keep multiple exact-object
requests active for one pull without adding a peer frame or changing FileId binding. The effective
window is the minimum of the process `--max-sync-tree-lanes` cap, the signed namespace
`maximum-lanes`, and the signed namespace `maximum-outstanding-requests`. Each active lane owns one
request ID, FileId, source, staging path, expected byte length, offer, and terminal transfer proof.
Failure, cancellation, or source loss settles every affected lane explicitly; branch and workspace
effects remain unavailable until the full authenticated graph closure is complete.

ADR 0330 commits completed file lanes through one strict CAS importer call per bounded window and
retires exact FileIds so a late offer cannot escape into the generic paused-file lane. ADR 0331 then
removes the remaining whole-store scan per window without changing this peer contract. A pull owns
one opaque verified in-memory CAS view, extends it only after digest/size verification and
no-replace durable installation, and performs a fresh strict full-store scan under the same
namespace transaction that accepts branches and projects the worktree. Concurrent serialized jobs
may add valid immutable objects; cached objects may not disappear or change, and the complete final
store must remain within quota. Status exposes scan and inspected-object counters. The cache is not
durable state, authority, or a substitute for the final effect fence.

Projection recovery is crash-forward. The local writer signs a pending workspace before the
complete derived directory is atomically exchanged, then signs stable only after the new side is
durable and validated. On startup, every configured writable/bidirectional tree-v2 namespace with
a pending workspace is reconciled before its sync worker or network service is made active. Exact
pre-exchange and post-exchange layouts retain their existing joins. ADR 0322 additionally accepts a
post-exchange tree whose reserved projection marker names the pending manifest and whose scan is
structurally valid but locally changed, provided any retained staging tree is the exact expected
active side. The edit is preserved and published as a later forward generation. A changed
active-marker tree or changed/unknown staging side remains ambiguous and fails closed. Processes
holding descriptors into the old directory across exchange are not covered by this path contract.

ADR 0337 makes signed-metadata authentication a startup invariant rather than
an incidental consequence of later work. Before a configured tree-v2
namespace reaches worker or network exposure, Agent startup authenticates the
current branch-pointer to immutable-record to manifest closure, every present
signed workspace record, and the signed maintenance record under one
namespace transaction. Byte-invalid state is retained exactly and startup
fails; it is never reinterpreted as absence.

`sync-repair` begins with the same five-root authentication and reports
`metadata=verified` only after it succeeds. Its repair behavior applies to
digest/size-invalid immutable content objects through the separately defined
quarantine path. It does not quarantine, delete, fetch over, or rewrite signed
metadata. An operator must restore reviewed byte-exact metadata externally,
after which the ordinary signature, namespace, and closure checks still
apply. This detects corruption, not a valid-old rollback; ADR 0314 owns
freshness for those semantic roots.

## Checkpoint branch record — `IOTXTVB1` format 2

The existing branch body remains 192 bytes plus 72 bytes per observation and a 64-byte signature.
Only byte 8 changes from ordinary version 1 to checkpoint version 2. A checkpoint has a zero
`previous` digest and carries one canonical observation for every writer in the exact frontier it
subsumes, including the checkpoint writer's prior generation when that writer is not at genesis.
It uses distinct version-2 signature and record-digest domains.

A checkpoint is valid only over a verified, conflict-free merged frontier. Its manifest
re-originates the complete projection at the new local checkpoint generation. It is an
authenticated graph floor: receivers fetch and verify the checkpoint record and manifest, but do
not recursively request records named by its observations. Those observations remain causal claims
inside the authorized checkpoint writer's signed attestation, not independently replayable
proofs or object-fetch roots. A receiver with no earlier local branch may bootstrap directly from a
valid checkpoint; it is trusting that authorized writer's compact snapshot. This is not
multisignature frontier agreement and does not constrain a malicious authorized writer beyond the
ordinary namespace policy.

An ordinary version-1 successor may name the checkpoint's exact record as predecessor. Thus peers
that negotiate bit 31 continue normal branch exchange above the floor; peers lacking bit 31 fail
closed before inventory rather than interpreting incomplete history.

Tree-v2 does not use auxiliary workers, content-v2 availability, range bundles, chunking, or
multiple simultaneous file lanes. Those require new negotiated policy; they are not inferred from
types 20--31.

## Owner-local retained-history recovery

ADR 0294 adds no peer message. Local-control v1.52 can authenticate and inventory live retained
branch records, compare exact candidate sets, and summarize current or historical conflicts. It can
also construct a restore-plan commitment over canonical policy, authenticated maintenance state,
the current multi-writer frontier and merged manifest, signed stable workspace generation, clean
worktree scan, selected record, and every required file object.

Forward restore never installs the selected record as a branch pointer. After exact plan revalidation,
the local writer creates one new manifest at its next generation. Each selected target value is
re-originated at that generation; every currently visible path absent from the target receives a new
local tombstone. The new head names the current local record as `previous` and the exact other-writer
frontier as observations. Normal immutable-first branch acceptance and journaled worktree projection
then apply. A target with concurrent candidates is refused rather than projected into an implicit
resolution. See `sync-time-machine.md`.

## Recipient-local sparse custody

ADR 0295 changes no message above. The subscriber still fetches and verifies the complete reachable
branch-record and manifest closure, including digest/size consistency for every file declaration.
Its owner-local canonical include/exclude prefixes decide which file-object requests are scheduled.
If one digest appears at selected and unselected paths, one verified local copy satisfies the
selected need. An unselected-only digest is not requested.

Accepting signed branch metadata does not claim possession of every file object it names. A later
request to a sparse publisher receives the ordinary exact absent/unavailable result when that source
does not hold the object; branch authority and object availability remain distinct. No remote frame
contains an interest rule or destination path.

Local-control v1.53 operations 120--121 inspect/replace/clear the recipient policy. Pull status,
repair, and GC expose complete/partial custody plus declared/selected/skipped counts. GC roots all
reachable signed metadata and only selected content. The worktree marker binds the manifest and
local policy so the first scan after a change preserves formerly unprojected absence; a successful
pull and journaled exchange establishes the new marker. See `sync-sparse-custody.md`.

## Exact-probe complementary sources

ADR 0296 also changes no peer frame. One primary publisher supplies the inventory/frontier.
Additional independently authorized primary-lane publishers may answer the same existing exact
object requests. `offered` uses the normal FileId-bound transfer; `absent` or `unavailable` advances
that immutable object to the next untried online source; `denied`, binding drift, or source exhaustion
fails closed. Bytes from any source receive the same digest, size, canonical decode, and CAS checks.
No additional source can replace the frontier or author/activate state.

The historical local-control operations 87--88 now admit content-v2 or tree-v2 jobs without changing
their values. `sync-pull-multi` registers all sources before the primary frontier request leaves;
`sync-source-add` extends one active job. Source count and exact probe/result/disposition counters are
content-free local status. Routed operation 90 remains content-v2-only.

## Durable local health

ADR 0297 adds no peer frame. Local-control v1.54 operation 122 either verifies the cached
stable-device-signed health record or refreshes it under the namespace transaction. The fixed
content-free observation binds the exact local policy, selected object coverage, merged frontier,
workspace/worktree convergence, conflicts, cutoffs, automation streak, active-store headroom, and
last runtime exact-probe source evidence. Sparse selected custody can be green while explicitly
partial. `rollback-witness=0 backup-certified=0` is part of the rendered contract.

## Optional semantic-state rollback witness

ADR 0314 changes no peer frame. When `--witness-sync-guarded-state` is selected, each tree-v2
namespace has a separately enrolled lane-10 service record under a namespace-derived domain. Its
semantic digest binds immutable storage identity, the sorted live branch frontier, and the exact
signed workspace and maintenance records. A stable-device-signed local two-head guard plus the
namespace transaction makes every authoritative root change crash-forward across the external
pending/committed compare-and-swap. Startup reconciles every namespace before RuntimeTree, and
root-derived effects recheck the last authenticated head while holding that transaction.

This is startup/mutation freshness for those semantic roots. It is not a continuous clone lease and
does not witness health, worktree bytes, object availability, quarantine, replay caches,
projection-marker/current-pointer state, content custody, backup, or permanent deletion safety.
