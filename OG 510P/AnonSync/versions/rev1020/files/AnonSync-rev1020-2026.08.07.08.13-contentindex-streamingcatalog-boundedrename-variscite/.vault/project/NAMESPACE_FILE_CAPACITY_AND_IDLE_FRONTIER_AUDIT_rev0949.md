# Namespace, file-capacity, and idle-frontier audit — rev0949

## Scope

This audit follows the shipping path from observer limits through folder-owner
composition, linked-service configuration, CLI/provisioning serialization,
runtime reports, and tests. It asks whether each bound names one resource and
whether an optimization can silently perform more whole-state work than the
cooperative scan scheduler intends.

## Finding 1: `maximum_entries` conflated namespace work and durable file state

The rooted walker increments its entry count for directories and every child
object before deciding whether the child is a synchronizable regular file. The
catalog and payload store, by contrast, retain regular-file identities and
history. Binding the walker entry count to their 100,000-row production ceiling
made directories and ignored objects consume file capacity. This was a contract
error even when no memory corruption or partial mutation occurred.

The correction is a two-dimensional limit:

| Dimension | Default | Hard validation ceiling | Spent by |
|---|---:|---:|---|
| namespace entries | 262,144 | 1,000,000 | every classified object |
| regular files | 100,000 | 1,000,000 | descriptor-classified regular files |
| delivered files per segment | 4,096 | 1,000,000 | eligible visitor callbacks |

Only the 100,000 regular-file and remote-path values are composed against the
production catalog and payload-store capacities. The 262,144 entry value remains
a work/memory defense. It does not imply that every possible 100,000-file tree
shape is admissible.

## Finding 2: a resume cursor could not be allowed to hide whole-folder excess

A naive regular-file counter that increments only for delivered suffix paths
would let each segment see at most 4,096 files while a much larger folder
eventually crosses the durable owners. Rev0949 increments the whole-walk file
count immediately after regular-file classification, including paths skipped by
the durable cursor and the first path that triggers a scheduling stop. Every
invocation therefore re-establishes the folder-wide file ceiling from the root.
This costs prefix work but preserves the current scanner's conservative capacity
truth until an indexed owner replaces that repetition.

## Finding 3: idle optimization duplicated bounded authoritative work

The idle path attempted a complete tree proof and learned it was too large only
when the segment frontier stopped it. It then ran the ordinary durable segment.
The correction gates on `catalog_hints.entries.size()` before taking a replica
snapshot or projecting current file rows. Total mappings are used because
tombstones still require exact path inspection. This bounds duplicate
optimization work; it does not redefine absence authority.

## Finding 4: the report could not distinguish why continuation occurred

The former boolean `completed` described the scheduling outcome incompletely.
Rev0949 adds an exact enum and JSON spelling for byte-frontier, path-frontier,
and end-of-namespace outcomes. The enum is assigned after rooted re-attestation.
It remains diagnostic and is deliberately absent from the durable epoch proof.

## Runtime and composition proof

Compiled tests cover:

- independent entry and file-limit validation, including zero and hard maxima;
- a directory spending namespace capacity without spending file capacity;
- cursor replay counting toward the whole-folder regular-file cap;
- folder-owner composition against catalog and payload capacities;
- rejection before catalog mutation when either dimension is exceeded;
- a two-file/one-directory tree under independent limits;
- known-large unchanged and tombstone-heavy catalogs bypassing idle proof;
- exact count, byte, and end-of-namespace stop reasons;
- linked-service JSON, provisioning, CLI, status, and `check-config` wiring.

## Remaining expensive boundaries

1. Immediate directory components are retained and sorted as one vector. A flat
   directory can still allocate in proportion to all of its names before a
   4,096-path segment stops.
2. Segment continuation replays the root prefix. Fairness is semantic, not
   asymptotically efficient.
3. Completed-epoch absence adjudication is whole-catalog work, including retained
   tombstones.
4. Payload inventory remains restart-cold and namespace-scanning.
5. Historical catalog/payload retention has no collector or bounded restore
   policy, so current-file capacity is not sustained-churn capacity.
6. The default watcher has its own topology/watch ceilings and remains an
   accelerator only.

## Recommended refactor order

1. Add a crash-consistent exact metadata/subtree index with monotonic change
   sequence and an explicit rebuild path.
2. Move continuation from repeated root replay to indexed successor/subtree
   scheduling while retaining component-path authority.
3. Make completed-epoch absence candidates incremental, then revalidate them
   through the rooted scanner before deletion publication.
4. Add a durable payload metadata index and rotating byte scrub.
5. Design version retention, restore, reachability pins, quarantine, and garbage
   collection as one recovery contract.
6. Qualify the first named Resilio workflow before raising defaults again.
