# Rev0987 bounded selective sync and rooted dematerialization audit

## Product correction

Rev0987 implements the first vertical selective-synchronization path in the
shipping Linux/headless C++ product. Selection is no longer a future design
claim: the configured folder catalog owns one durable bounded policy, the
requester sends that exact policy over reconciliation protocol generation 4,
the serving peer withholds excluded payload bytes, and ordinary convergence can
later acquire and publish the selected bytes.

The product meaning is deliberately narrow and explicit:

- `materialize` retains causal metadata, obtains the exact payload, and
  publishes the visible regular file beneath the configured rooted folder;
- `metadata_only` retains causal metadata but neither requests nor publishes
  the file payload; and
- tombstones remain metadata and continue through ordinary convergence.

This is not a placeholder filesystem. An excluded file has no synthetic rooted
entry. Policy and causal state are visible through the owner CLI and durable
catalog, not through an emulated sparse file.

## Bounded policy

The policy is one default mode plus at most 1,024 unique canonical
component-prefix rules containing at most 48 KiB of path bytes. Longest matching
component prefix wins. Policy generation and digest are durable local authority.

The policy is not one row per synchronized path. A multi-terabyte tree may
contain many more paths than a human selection contains prefixes. Rooted
observation evaluates the bounded policy without allocating per lookup and
prunes a metadata-only directory before enumerating its descendants when no
deeper materialize rule exists.

The directory-pruning audit found a subtle lexical defect in the first
allocation-free refactor. Lower-bounding on `directory` itself is not equivalent
to lower-bounding on the virtual key `directory/`: a legal unrelated sibling
such as `directory-archive` sorts before `directory/keep` and could hide the
deeper include. The retained implementation compares against the virtual
slash-suffixed key without constructing it, and the focused regression uses
that adversarial ordering.

## Durable catalog and policy control

Folder-catalog schema v6 stores the selection generation, default mode, digest,
absence-fence generation, and bounded rule table. Selection replacement is an
offline owner operation:

```text
anonsync_sync selective-sync-status --manifest ABSOLUTE_JSON
anonsync_sync selective-sync-set --manifest ABSOLUTE_JSON \
  --default materialize|metadata_only \
  [--rule MODE=CANONICAL_PATH ...]
```

Both operations claim the deployment singleton. They inspect or mutate only
the configured folder catalog; they do not open the synchronized root, payload
store, replica database, or network. Duplicate, malformed, over-count, and
over-byte policies fail before mutation. Semantic replay is idempotent.

Every real policy change resets the bounded local-scan and remote-work cursors.
A deletion-inference fence is opened only when the new policy materializes at
least one canonical path that the old policy treated as metadata-only. Pure
narrowing cannot expose a hidden absence, so it no longer globally delays
ordinary deletion repair for unrelated selected paths. If a prior expansion
fence is already active, later edits retain the fence until an ordinary complete
remote sweep settles it.

## Wire omission and later acquisition

Protocol generation 4 binds the complete requester policy into the canonical
request digest. The response explicitly lists every returned file operation
whose payload was omitted because the requester selected `metadata_only`.
Validation requires that list to be sorted, unique, bounded by the operation
page, refer only to returned file operations, and exactly match the request
policy. A metadata-only operation cannot smuggle payload bytes; a selected file
cannot be admitted without the existing payload-before-metadata rule.

The reconciliation service admits metadata-only causal operations without
creating payload objects. TLS and one-shot accounting report the count. After a
genuine selection expansion, ordinary reconciliation requests the missing
payload and ordinary folder convergence publishes the file. No second transfer
or restoration engine exists.

## Safe rooted dematerialization

Changing a path from `materialize` to `metadata_only` now has a physical
meaning for an already synchronized regular file. Ordinary convergence may
remove the rooted copy only when all of the following remain exact:

1. the current policy generation and digest still classify the path as
   metadata-only;
2. the catalog maps the path to an exact retained file operation;
3. the rooted descriptor still matches that catalog entry byte-for-byte and by
   POSIX observation;
4. the current sole-visible causal target is that operation or its proven
   successor;
5. an independently verified immutable private payload descriptor for the
   catalog predecessor is retained through the unlink; and
6. the visible name is atomically displaced to a private name, that exact
   displaced inode is opened no-follow and hashed again in full, and its
   complete POSIX observation remains stable through the final unlink; and
7. the causal target, catalog entry, policy, rooted identity, and final absence
   are re-proved at the publication cutpoints.

The second hash matters because metadata reproof alone is not complete-byte
authority. A digest, read, or observation failure before the private unlink
attempts to restore the exact displaced object to its visible name. This
prevents selective sync from deleting an untracked file, a locally changed
file, a conflict, or the only proved copy. If the private predecessor payload is
missing, dematerialization is blocked and the path remains unresolved. The
operation and catalog evidence remain; no tombstone is minted.

This first destructive slice deliberately pays a second complete read of the
rooted file: the convergence observation hashes the visible descriptor, and the
atomic remover hashes the displaced private inode again. That is O(1) memory but
can be expensive for very large files; eliminating the duplicate read requires
a shared content-proof capability rather than weakening the final byte fence.
A process crash after atomic displacement and before restoration or unlink may
leave a publication-shaped private recovery residue while the visible name is
absent. The bytes remain on disk and the independently retained payload remains
available, but rev0987 provides no automatic residue recovery for this narrow
window. The rooted observer ignores that reserved artifact instead of publishing
it as a user file. This is a durability and disk-hygiene nonclaim, not deletion
authority over the residue.

Dematerialization consumes the existing bounded remote-effect frontier. A
large policy narrowing therefore removes at most the configured number of
operations in one pass and resumes through the durable remote-work cursor.
Changed and untracked collisions remain rooted and unresolved rather than
being converted into policy success.

Dematerialization reclaims synchronized-root space, not total AnonSync storage.
The immutable private payload is intentionally retained. Quota-aware payload
collection and garbage collection remain separate future authority.

## Reselection and causal successors

A metadata-only peer may learn a newer remote operation while its old rooted
predecessor is absent. Reselection must not require the intentionally removed
predecessor to reappear first. While the exact expansion fence is active,
ordinary remote apply may materialize either the cataloged head or a current
causal successor. The usual sole-visible, causal-supersession, payload,
catalog, policy, and rooted publication checks remain mandatory.

The focused regression proves this complete sequence:

1. materialize a first remote value;
2. narrow selection and safely remove the rooted predecessor;
3. admit a newer remote causal successor while the path remains metadata-only;
4. expand selection; and
5. acquire and publish the successor, then settle the expansion fence through
   the ordinary sweep.

## Stale in-flight authority

Selection is re-proved at each rooted publication seam. A local scan prepared
under an older policy cannot publish after narrowing. Direct remote apply and
historical restore reject metadata-only paths before payload or rooted effect
authority and re-prove the exact generation and digest before publication.
This prevents a stale in-flight scan, remote apply, or restore from rematerializing
an excluded path after the operator changed policy.

The deployment singleton is still the supported cross-database service-stop
boundary for policy mutation. These lower-level checks are defense in depth and
make accidental in-process misuse fail closed.

## Multi-terabyte memory boundary

The new selection state is bounded independently of tree size:

- at most 1,024 rules and 48 KiB of canonical rule paths;
- no per-file selection rows;
- no namespace walk to decide whether a policy is an expansion;
- no heap allocation in ordinary path-mode and directory-pruning decisions;
- no namespace walk or temporary merged rule vector to classify expansion;
- traversal prunes fully excluded subtrees before descendant enumeration; and
- existing persisted scan/apply cursors continue to bound work and rooted
  dematerialization effects per pass.

These are structural bounds, not a target-scale RSS proof. The retained model,
catalog, payload identity, and remote projection still have explicit finite
capacities, and the sanitizer folder-owner suite remains memory-heavy. A real
multi-terabyte, high-path-count soak with measured peak RSS and disk behavior is
still required before claiming workload qualification.

## Deliberate limitations

Rev0987 does not provide placeholders, per-device cloud-style availability
badges, quota-based automatic eviction, payload garbage collection, Android
storage/lifecycle integration, identity-preserving rename/move, empty-directory
semantics, complete portable metadata, or ordinary conflict UI. Metadata-only
is a causal and transfer policy for regular files, not a claim that every
Resilio selective-sync user experience is complete.

Android remains a desirable later adapter. The Linux owner depends on rooted
POSIX descriptors, advisory leases, SQLite, and an always-running service.
Termux or app-private Linux can be a portability experiment, but supported
Android requires explicit scoped-storage and foreground-service ownership.

## Evidence boundary

The focused policy, folder-owner, protocol, reconciliation-service, TLS,
sync-once, local-control, and configured-folder process regressions are the
semantic oracles for this slice. Compiler, sanitizer, full-registry,
reconstruction, and package evidence remain independently load-bearing.

`tools/audit_sync_replica_selective_sync.py` is a lexical source-shape audit.
It cannot prove filesystem identity, race freedom, allocation behavior,
cryptography, durability, crash recovery, throughput, target-scale memory, or
Android behavior.
