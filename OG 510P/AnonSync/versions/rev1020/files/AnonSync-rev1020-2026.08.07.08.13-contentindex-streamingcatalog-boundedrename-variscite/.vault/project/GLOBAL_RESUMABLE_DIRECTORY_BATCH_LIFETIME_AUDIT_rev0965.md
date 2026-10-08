# Global resumable directory-batch lifetime audit — rev0965

## Heart of the mission

AnonSync exists to replace Resilio Sync with one dependable C++ folder-sync
application. Large and deeply nested real folders must remain repairable under
bounded memory, restart, watcher loss, and ordinary namespace mutation. A
per-directory bound that silently multiplies at every active recursion depth is
not an adequate production bound.

## The defect

Rev0964 replaced whole immediate-directory materialization in the shipping
resumable scanner with exact bytewise batches of at most 4,096 selected
basenames. That removed the flat-directory allocation cliff, but the recursive
walk retained the unprocessed parent batch while descending into a child.
A pathologically deep tree could therefore retain one full batch at every
active depth. With the configured depth frontier, the nominal 4,096-name bound
was only a per-frame bound rather than a traversal-wide bound.

The retained parent vector was also mostly waste. Once the walker had opened and
attested the selected child directory, recursive preorder needed only the child
component, its canonical path, the opened descriptor and observation, and the
component boundary from which to resume the same parent. The remaining selected
parent strings could be selected again from the still-open parent directory.

## Corrected C++ ownership shape

The resumable path now splits component processing into three explicit pieces:

1. `walk_component_batch_until_directory_or_throw` classifies regular files
   until it reaches the first directory, then returns descriptor-owning pending
   descent state.
2. The caller destroys the selected parent vector, including its reserved
   capacity, and retires its diagnostic accounting before recursion.
3. `walk_pending_directory_or_throw` descends through the retained descriptor,
   reopens the child from the parent afterward, and proves the same directory
   identity before the parent walk resumes strictly after that component.

`PendingDirectoryDescent` owns its descriptor through `ScopedFd`. Component and
canonical-path strings are allocated before the child is opened; after the open,
all transferred members are no-throw movable. Allocation, classification,
recursive, or rebinding failure therefore cannot leak the child descriptor.
The non-resumable complete observer uses the same classifier and rebinding
functions but intentionally keeps its whole immediate-directory vector.

## Traversal-wide selected-name bound

`ScopedBufferedDirectoryComponentBatch` accounts every live selected basename
batch in the resumable path. Before `read_next_sorted_component_batch_or_throw`
reserves the next selector vector, the resumable loop requires the live selected-
name count to be zero. The RAII constructor repeats that no-overlap invariant,
updates both the pre-existing largest individual-batch diagnostic and a new
`peak_simultaneously_buffered_directory_component_count` diagnostic, and retires
the exact count on every return or exception path. The public entry point proves
that the live count is zero after traversal. The boundary therefore constrains
actual allocation lifetime, not merely a diagnostic sampled after allocation.

Because a parent batch is released before child selection begins, selected
basename storage is globally bounded to one 4,096-name batch for one traversal.
This does not make all traversal memory constant. Each active depth still owns a
directory stream/descriptor and pending component/path observation. The number
of those records is depth-indexed, but aggregate string bytes also depend on the
length of every retained canonical path and are not claimed to be a strict
O(depth)-byte bound. The selected-name bound also does not count allocator
overhead, although POSIX component limits bound each retained basename.

## Exact parent resumption and preorder

The walk retains the same open parent directory across child descent. On return,
it re-enumerates names strictly greater than the processed directory component.
This preserves the existing component-wise bytewise preorder: the complete child
subtree is visited before later siblings. Regular-file callback and durable
cursor semantics are unchanged. A callback still advances the in-memory cursor
only after it succeeds, so a thrown callback is replayable.

The tradeoff is deliberate: a directory with many child directories can incur
another complete `readdir` pass after each child. Rev0965 removes depth-multiplied
name retention; it does not claim an indexed directory, skipped-prefix
elimination, or improved asymptotic enumeration cost.

## Census drift correction

Releasing a parent batch increases the importance of the parent rescan boundary.
The first charged census already records the exact number of eligible components
remaining in that directory invocation. Rev0964 fenced growth only when extra
work survived after the budget reached zero. A deletion, or a rename from the
unprocessed suffix to before the processed child component, could instead make a
later suffix smaller. Returning `EndOfNamespace` from that shortened rescan
would falsely claim a complete epoch even though a current name could have moved
behind the cursor.

Every non-initial parent rescan now requires its exact eligible suffix count to
equal the remaining first-census count before processing any selected name.
Detected growth, shrinkage, or a rename across the component boundary returns
the non-complete `directory_census_frontier` outcome. The folder owner
consequently withholds completed-epoch absence and deletion authority and starts
a later ordinary epoch from fresh observation.

This is a cardinality fence on required rescans, not snapshot isolation. A
change after the final required pass, or equal-cardinality mutation that remains
wholly on one side of a processed boundary, may still be observed as an
asynchronous namespace state. Rooted `lstat`, child open/rebind identity,
callback idempotence, watcher wakeups, and later complete epochs remain the
repair model.

## Mechanical regressions

The focused observer test constructs two nested directory levels, each with one
leading child and 4,095 regular-file siblings, plus a deepest leaf. The complete
8,191-file preorder requires five directory enumeration passes, reaches every
file exactly once, charges 8,193 namespace entries exactly once, and reports:

- largest individual selected batch: 4,096;
- largest simultaneous selected-name count: 4,096, not 8,192;
- exact two-directory rooted traversal and post-walk identity reproof.

A second regression starts with `m-child/leaf.dat` and `z-later.dat`. During the
child callback it renames the later parent file to `a-moved.dat`, crossing behind
the released parent boundary without changing total root cardinality. The first
walk returns `directory_census_frontier` and cannot manufacture completion. A
fresh epoch then observes `a-moved.dat` followed by the child leaf in exact
preorder.

The older 4,097+17 growth regression was strengthened: an inconsistent second
census now publishes none of its selected names. The durable cursor remains at
the last name from the coherent first batch, and the next segment discovers the
interleaved name, displaced original member, and every appended suffix exactly
once.

## Adjacent audit and contamination correction

A clean adjacent rebuild exposed unrelated retained-version prototype edits in
the folder-owner header, implementation, regression, and low-level replica CLI.
They were not part of the selected slice; the folder-owner branch did not compile
against the sealed interface, while the CLI branch silently widened the product
surface. All four files were restored byte-for-byte and mode-for-mode from the
verified rev0964 archive. Parent comparison then proved that only the intended
observer source, header, and regression differed before documentation and
release-policy work. No result from a stale pre-restoration binary is release
evidence.

The cloudtainer audit also found an obsolete cleanup loop from a discarded
rev0965 validator. Its pathname-wide process match sent termination signals to
current rev0965 Ninja, CTest, and test processes. That loop interrupted product
validation and made one missing-object link result orchestration-contaminated.
It was removed, compiler activity was allowed to quiesce, the affected link was
reissued, and every affected test shard was rerun. Interrupted invocations are
retained only as negative orchestration evidence and are excluded from release
authority.

## Complexity and remaining waste

For a directory containing N eligible components and a selected bound K, each
selection pass is O(N log K) comparisons and O(K) selected-name storage. Releasing
before every child can increase the number of passes substantially. Deep trees
retain O(depth) descriptors and path state but no longer O(depth × K) selected
names. The complete non-resumable observer still materializes and sorts each
immediate directory and may retain ancestor vectors.

A durable subtree/name index remains the honest route to eliminating repeated
large skipped-prefix enumeration. Huge-tree qualification must measure RSS,
allocator behavior, directory-pass counts, latency, watcher loss repair, and
moving-namespace convergence on the named uninstall workload.

## What this proves

Rev0965 proves that the shipping resumable walk:

- never simultaneously retains more than one selected basename batch;
- preserves rooted component preorder and post-child identity reproof;
- owns pending child descriptors exception-safely;
- does not double-charge namespace capacity during parent rescans;
- denies completion when exact suffix cardinality drifts across a rescan; and
- preserves restartable cursor and completed-epoch deletion fences.

## What this does not prove

This revision does not provide a point-in-time filesystem snapshot, durable
subtree index, rename identity, empty-directory synchronization, user version
history, garbage collection, target-scale huge-tree qualification, or a
process-wide constant-memory claim. The non-resumable observer remains a whole-
directory implementation. Namespace mutation is repaired by conservative
frontiers, watcher notifications, rooted reproof, and later epochs rather than
by claiming snapshot semantics the filesystem does not provide.
