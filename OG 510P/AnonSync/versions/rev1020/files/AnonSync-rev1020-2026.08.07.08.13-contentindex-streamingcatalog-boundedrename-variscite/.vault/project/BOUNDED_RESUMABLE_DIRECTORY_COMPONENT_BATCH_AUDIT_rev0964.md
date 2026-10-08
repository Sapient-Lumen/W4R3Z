# Bounded Resumable Directory Component Batch Audit — rev0964

## Heart of the mission

AnonSync exists to replace Resilio Sync with one practical C++ folder-sync
application. A durable continuation cursor is useful only if a large ordinary
folder can be revisited without turning each bounded service turn into an
unbounded memory event. Rev0947 made local scan progress fair, and rev0948
bounded delivered callbacks and journal rows, but the shipping observer still
read every immediate basename into one `std::vector<std::string>` before it
could deliver even one file. A flat directory near the 262,144-entry namespace
ceiling could therefore allocate and sort the whole component set on every
4,096-path segment.

Rev0964 removes that flat-directory memory cliff from the resumable production
walk. It does not create another index, scanner, scheduler, or deletion owner.
It changes the component-selection implementation beneath the existing rooted
observer while preserving the same traversal order, continuation cursor,
namespace ceilings, callback cutpoint, and completed-epoch absence rules.

## The defect

The previous `walk_directory_or_throw` always called
`read_sorted_components_or_throw`. That helper:

1. consumed the complete directory stream;
2. copied every non-dot `d_name` into a vector;
3. charged each entry against `maximum_entries`;
4. sorted the complete vector; and only then
5. classified the first component.

The 4,096 delivered-file frontier therefore bounded callback and journal work,
but not the immediate basename allocation or sort. The same complete vector was
rebuilt after each persisted scan cursor. This was especially wasteful for flat
folders containing many zero-byte or small files—the exact shape rev0948 was
intended to make schedulable.

This was not merely cosmetic allocation. The supported namespace ceiling is
larger than the production path frontier by two orders of magnitude, and a
basename may approach the filesystem's component limit. A direct whole-vector
implementation made memory scale with the largest single directory before any
useful path effect could complete.

## Corrected C++ shape

The resumable branch now selects one exact bytewise-lexicographic component
batch with a bounded max-heap:

- `kSyncReplicaFolderTraversalMaximumBufferedDirectoryComponentsPerBatch` is
  fixed at 4,096 and is not a user-visible policy knob;
- one complete `readdir` pass retains only the lexicographically smallest 4,096
  components strictly after the current in-directory batch boundary;
- unselected names are compared through `std::string_view`, avoiding a heap
  allocation for every discarded candidate;
- one reserved `std::vector<std::string>` is maintained as the max-heap, sorted
  in place with `std::sort_heap`, and moved directly into the batch; no second
  copy-out component buffer coexists;
- the batch is processed through the shared `walk_component_batch_or_throw`, so
  regular-file classification, rooted directory descent, callbacks, cursor
  advancement, and post-walk directory rebinding remain one implementation;
- the first pass's eligible-component cardinality becomes a non-growing work
  fence for that directory visit, so later rescans cannot chase an unbounded
  suffix created concurrently;
- if a later pass sees eligible names beyond that first census, the traversal
  returns the non-complete `directory_census_frontier` outcome rather than
  manufacturing end-of-namespace authority from a moving namespace;
- another full directory pass occurs only when names remain inside that census
  fence and the current traversal segment still has useful delivered-file
  capacity; and
- the non-resumable complete observation/visitor branch deliberately retains
  the old complete-vector implementation. Rev0964 changes the shipping
  restartable scan path, not every observer mode.

The resulting selection is exact for a stable directory. For any boundary
`after_component`, the max-heap contains the smallest `min(4096, N)` eligible
names. Replacing the current largest retained name whenever a smaller candidate
appears is equivalent to sorting all eligible names and taking their prefix,
but requires storage proportional to the fixed batch rather than `N`.

## Preserved traversal order

AnonSync's continuation order is component-wise bytewise preorder, not a flat
path-string sort:

- immediate components are ordered by basename;
- a directory's complete subtree is visited before its next sibling; and
- the persisted cursor compares path components with
  `sync_replica_folder_traversal_path_less`.

Batching occurs only between immediate components of one already-open
directory. Every selected batch is sorted before processing, recursive descent
still completes before the next selected sibling, and the next batch begins
strictly after the previous batch's last basename. No second traversal order or
cursor grammar is introduced.

## Entry and file capacity accounting

The first enumeration pass for each directory visit still charges every non-dot
entry it observes against `maximum_entries`, including directories, symbolic
links, special files, and internal publication residues. Later selection passes
over the same open directory do not double-charge that census. This preserves
the pre-rev0964 interpretation of the namespace ceiling and prevents the batch
implementation itself from exhausting the budget merely by rereading names.

The exact eligible-component count from that first pass is also retained as a
non-growing processing budget. Each completed batch subtracts its actual
component count, and a later pass may request no more than the remaining first-
census count. Concurrent insertions may displace an unprocessed name in an
asynchronous sweep, but they cannot lengthen the visit or create an unbounded
rescan chase. Names not reached are ordinary later-epoch work.

Every selected regular file, including a cursor-skipped file, is still
`fstatat(..., AT_SYMLINK_NOFOLLOW)` classified and increments the independent
whole-walk regular-file counter. The delivered-file frontier remains separate:
skipped files do not spend the 4,096 callback allowance, but they cannot let a
persisted cursor bypass the configured 100,000-file production capacity.

The entry accounting is an asynchronous first-pass census, not snapshot
isolation. As before, namespace mutation during a sweep is repaired by later
epochs and watcher notifications; completed-epoch absence remains fenced by the
catalog and rooted reproof machinery. Rev0964 does not claim a simultaneous
directory snapshot.

## Root and directory authority

The refactor does not weaken the descriptor-rooted boundary:

- the retained root is independently opened and matched to its device/inode;
- the root mount identity and resolution capability are captured and retained;
- every child is classified with no-follow `fstatat` beneath the open parent;
- every directory descent uses the existing no-symlink, retained-root-mount
  resolver;
- the opened child directory is reopened through its parent after the complete
  recursive walk and must retain the same directory identity; and
- the retained root is verified again before a segment can return.

A callback may still make durable progress before a later traversal failure.
That is the existing contract: callbacks must be idempotent and a scan cursor is
published only after the complete path effect succeeds.

## Diagnostics without authority

`SyncReplicaFolderTraversalSegment` now reports:

- `directory_enumeration_pass_count`; and
- `peak_buffered_directory_component_batch_count`.

These values prove which implementation shape ran and make repeated name-pass
cost visible to tests. They do not authorize a cursor, deletion, catalog
publication, or filesystem effect. The second value is the largest individual
batch, not total process allocation: recursive descent can retain one bounded
batch for each active directory depth, which remains separately capped by the
configured depth ceiling.

## Mechanical regression

The first focused observer regression creates 4,113 regular files—seventeen
more than the component batch limit—and converges them through three persisted
continuations. It proves:

- exact lexicographic delivery with no omission or duplicate;
- two regular-file frontiers followed by exact end-of-namespace completion;
- a largest individual component batch of exactly 4,096 on every invocation;
- one directory pass when the first path frontier stops inside the first batch;
- two passes when a later invocation must cross the batch boundary; and
- `visited_entry_count == 4,113` on every invocation, rather than charging the
  second enumeration pass twice.

A second regression starts with 4,097 regular files. From the first callback it
inserts one name between the first 4,096-name batch boundary and the last
original census member, plus sixteen later suffix names. The interleaved name
therefore consumes the one remaining bounded slot and displaces an original
first-census member. The first segment must return
`directory_census_frontier`, not `EndOfNamespace`, while retaining its last
delivered cursor. A continuation from that cursor then reaches the displaced
original and every inserted name exactly once. This binds the work fence, the
absence-authority fence, and the existing durable continuation contract.

The pre-existing observer race regression continues to replace a visited
directory at the count cutpoint and requires failure before success can be
returned. The folder-owner suite continues to prove durable 2+2+1 progress,
restart, journal publication, cursor semantics, and completed-epoch absence.

## Adjacent refactor findings

The first implementation draft exposed a field named as though 4,096 were the
maximum number of basenames retained simultaneously by the entire recursive
walk. That was too strong: an ancestor's unprocessed batch remains live while a
child directory is traversed. The final name and prose say **per batch**, and
the configured depth ceiling remains part of the actual aggregate-memory bound.

A later object-shape audit found that the bounded selector still used a
`std::priority_queue<std::string>` and then copied every selected name into a
second vector for sorting. That kept two O(K) component buffers live and briefly
duplicated the current heap top during extraction. The final implementation uses
one reserved vector for `push_heap`, replacement, `sort_heap`, and move-only
batch handoff. The documented per-batch bound now matches the actual container
shape rather than only its asymptotic order.

The audit then found that bounded storage alone was insufficient. A later
rescan could keep following names created after the first pass, while those
names were outside the already-charged census. Under continuous suffix creation,
the draft could perform unbounded directory work. The implementation therefore
retains the first eligible cardinality as a decreasing visit budget.

A second review found that the count fence alone was still insufficient. A new
name inserted just after the current batch boundary could consume the final
budgeted slot, displace an original census member, and let the function return
`EndOfNamespace` despite leaving an eligible path unvisited. That outcome could
feed completed-epoch absence logic. Rev0964 now returns
`directory_census_frontier` whenever the final budgeted batch reports more
eligible names. The cursor remains at the last delivered regular file, so a
later segment reaches the displaced member, while the moving namespace cannot
authorize deletion. The post-census insertion regression fails without both
the bounded-work and non-completion fences.

The audit also retained the old complete-vector helper only behind
`context.segment == nullptr`. Sharing classification and recursion in
`walk_component_batch_or_throw` avoids maintaining two subtly different
filesystem authority paths while making the remaining non-resumable allocation
boundary explicit.

## Complexity and remaining waste

For a stable directory with `N` immediate names and batch size `K`, one batch
selection uses `O(N log K)` comparisons and `O(K)` retained names. A traversal
that consumes multiple batches rescans the directory, so a complete large
single-directory segment can cost `O(N * ceil(N/K) * log K)` comparisons. The
number of processed components in one visit cannot grow beyond its first-census
`N`, even if the directory is concurrently extended. If later enumeration sees
additional eligible names, the visit stops non-complete instead of claiming the
namespace ended. The production delivered-file frontier is also 4,096, so
ordinary productive turns
usually consume at most one component batch after any replayed prefix, but a
large skipped prefix can require several passes.

Rev0964 therefore exchanges unbounded immediate-directory memory and `O(N log
N)` whole-vector sorting for bounded per-batch memory and potentially repeated
name enumeration. That is the right near-term product trade because it removes
a hard memory cliff without creating a new durable authority. It is not the
final huge-tree architecture.

The following remain open:

- every resumed segment starts at the root and repeats classification of its
  skipped regular-file prefix;
- each selection batch rescans a large immediate directory;
- recursive depth can retain one 4,096-name batch per active directory;
- the non-resumable complete observer still retains each immediate directory's
  complete name vector;
- the private payload namespace still needs a durable exact change-sequence
  index and rebuild/scrub contract;
- no large-tree RSS, latency, cold-cache, filesystem, or soak qualification has
  been performed; and
- user-restorable versions, retention, reachability, and garbage collection
  remain separate product gaps.

The next scale owner should be a crash-consistent exact metadata/subtree index
that can seek near a durable cursor while leaving the current rooted scanner as
its rebuild and rotating-revalidation oracle. An index hit must never manufacture
absence or bypass current rooted reproof.

## What this proves

Rev0964 proves that the shipping resumable folder walk no longer retains a flat
directory's complete basename set before making bounded progress and cannot
extend one directory visit beyond its first-census component count. A later
enumeration that observes extra eligible names cannot manufacture completion or
completed-epoch absence authority; the last delivered cursor remains available
to resume the displaced suffix. For a stable namespace the walk preserves exact
component preorder, path callbacks, capacity interpretation, rooted rebinding,
and continuation semantics while retaining at most 4,096 names in each
individual selected batch.

## What this does not prove

It does not prove constant total traversal memory, point-in-time namespace
snapshotting, optimal large-directory CPU or I/O, bounded skipped-prefix
metadata, a durable subtree index, cross-platform directory behavior, or target-
scale qualification. The lexical structural audit is not semantic authority;
compiler, runtime, sanitizer, race, package, and clean-extraction evidence remain
load-bearing.
