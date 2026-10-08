# Bounded remote inspection sweep and linear visible projection audit — rev0952

## Finding 1: apply bounds did not bound rooted inspection

The rev0951 planner admitted the complete remote projection and then opened every
sole-visible pathname before choosing a bounded apply segment. A projection that
was large but already satisfied, conflicted, missing payloads, or awaiting local
absence adjudication could therefore spend rooted descriptor work up to the
100,000-path admission ceiling in one pass. The durable cyclic cursor described
where effect selection resumed, but it did not prove that one stable projection
had been inspected exactly once across restarts.

Rev0952 adds an independent rooted-inspection frontier. Coverage persists only
with a basis digest over the exact catalog cutpoint and remote visible state. The
origin path and acknowledged count determine the expected current cursor; a
mismatch is corruption or incompatible state and fails before effects. The
unresolved flag is cumulative for the basis. A clean completion has no retained
sweep journal; an incomplete no-effect segment persists it; any selected effect
invalidates it because even an idempotent apply may advance catalog authority.

The complete projection remains a hard safety preflight. The new frontier bounds
filesystem inspection, not path/evidence admission. This preserves fail-closed
behavior for an invalid suffix while preventing valid large projections from
requiring one unbounded rooted turn.

## Finding 2: settlement lacked a complete rooted-coverage witness

A bounded final pass could previously observe no selected effects yet still have
a remote suffix it had not rooted-inspected. The process cutpoint now includes
the sweep journal, and final settlement requires a complete sweep with no
cumulative unresolved paths. Missing payloads, conflicts, tombstone conflicts,
and exact local absence awaiting a complete scan remain visible remainder.

The speculative idle proof is restricted to projections that fit the inspection
budget and cannot bypass a retained partial sweep. This keeps the optimization a
read-only proof rather than a second completion authority.

## Finding 3: bulk visible projection repeated global scans

The old bulk API first built a copied `std::set<std::string>` of distinct paths.
For each path it called `visible_path()`, which scanned all active operation IDs
again. With one operation per path, projection construction repeatedly walked
the complete active set and copied every key before producing its owned result.

The replacement performs one active-operation grouping pass into a sorted map
keyed by borrowed `std::string_view`, storing borrowed pointers to immutable
model-owned operations. A shared helper computes maximal visible operations,
primary selection, and preserved files for both single-path and bulk calls. The
public result still owns its path and operation IDs. Borrowing lasts only for the
const call and is documented on the lookup API.

This removes the paths-times-active-set rescan and duplicate path set. It does
not change the pairwise supersession comparison among operations on the same
path, and it does not eliminate complete projection materialization.

## Crash and concurrency reasoning

- Sweep state is stored in the same catalog database singleton as the fairness
  cursor and updated by one optimistic SQLite transaction.
- The basis authenticates catalog and remote visible state, not filesystem bytes.
  Rooted files are inspected in the segment that acknowledges them.
- Apply candidates borrow from an immutable restored model that outlives the
  candidate vector and is not mutated during execution.
- Progress publishes only after selected apply owners complete. An exception
  leaves the old journal/cursor; already completed effects change the catalog
  basis and force a conservative restart.
- Cross-owner reads remain sequential. Another process moving catalog or cursor
  state is detected by the exact reload/CAS-style update or by a changed basis.
- A filesystem mutation behind a completed segment is ordinary asynchronous
  next-scan work; this revision does not claim snapshot isolation across the
  rooted namespace.

## Remaining priority

The next scale owner should be a crash-consistent incremental metadata/subtree
and payload index with monotonic change sequence, bounded work queues, and rooted
complete rebuild plus rotating scrub. Retention, restore, and garbage collection
must be designed with snapshot/in-flight pins before payload deletion is allowed.
