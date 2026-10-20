# ADR 0331: Effect-fence cached tree-v2 CAS inventory

- Status: accepted, implemented, and Sandwurm scale-qualified
- Date: 2026-09-04

## Context

ADR 0330 reduced tree-v2 content-store inventory work from once per received file to once per
completed lane window. The exact cap-16 Sandwurm gate improved materially, but a 3,500-file follower
still performed 219 complete CAS walks. Because every walk opens, sizes, and SHA-256 verifies every
existing object, the residual work remained approximately quadratic in the number of objects divided
by lane width.

The tempting optimization—remember the first inventory and trust it until the pull finishes—would
be wrong. Pull callbacks release the namespace transaction between transport events. Another local
IoTox job can legitimately add immutable objects, and owner-controlled storage can remove, replace,
or corrupt a cached object. Quota admission based only on stale counters could also allow the final
store to exceed its signed namespace ceiling.

## Decision

Keep tree-v2 peer framing, FileId binding, object identity, branches, manifests, conflict semantics,
and workspace projection unchanged. Optimize only local CAS admission through an opaque, pull-owned
verified inventory:

1. The first completed file window strictly inventories the complete tree-v2 CAS under a namespace
   transaction. Every entry retains the existing name, type, ownership, size, and SHA-256 checks.
   Existing quota excess is rejected.
2. The resulting in-memory inventory is not a durable index and cannot be constructed as verified by
   an ordinary caller. Each subsequent window performs prospective quota accounting against that
   inventory, verifies any exact reused object, verifies every staging source by digest and size,
   and installs through the existing no-replace and directory-durability path. Successful installs
   extend the private inventory.
3. Before accepting any signed branch or projecting any worktree, the subscriber performs one new
   strict full-store inventory under the *same namespace transaction* as those effects. Every object
   remembered by the pull must still exist with its exact size and digest. Fully verified additive
   objects from another serialized job are permitted and included in final quota accounting;
   removal, replacement, corruption, malformed state, and quota drift fail closed.
4. A file-bearing pull therefore performs one initial strict inventory and one final effect-fence
   inventory, independent of its number of file-commit batches. A failed or still-active pull may
   have performed only its initial scan. Additional simultaneous pull jobs have independent caches
   and final fences.

`sync-status` reports aggregate `tree-cas-full-inventory-scans` and
`tree-cas-inventory-objects-inspected`, plus the corresponding counters on each retained tree job.
Three-writer capacity receipts bind both per-node counters. Their verifier requires follower scans
to remain bounded by pull sessions and, for multi-batch populations, strictly below commit-batch
count. This records the actual multi-job automation behavior instead of falsely assuming one global
pull.

## Consequences

The owned registry now proves cached two-batch installation, an exact final inventory, acceptance of
one independently verified additive object, and rejection after a cached object is corrupted. The
four-lane service pipeline proves one initial plus one final scan around a complete successful pull.

A clean source-linked cap-16 direct run of the 3,500-file campaign completed full custody, repair,
three-way conflict convergence, and explicit resolution. Followers committed 219 windows each but
performed only 7 and 5 full inventory scans across intermediate pull jobs caused by periodic
publication while the source population was created. Capacity catch-up took 379.948 seconds and
total time was 478.979 seconds: 1.8% faster and effectively flat respectively against ADR 0330's
prior direct sample. This demonstrates removal of repeated hashing—not a material end-to-end latency
win on that host sample. Host load, intermediate source publications, per-object Tox lifecycle, and
per-object durability remain confounders.

The exact fresh-state 2-vCPU/2-GiB networkless Sandwurm repeat then passed from clean source revision
`03e0996fef3f9b5b73288806c720e411106cae3c`. Followers again committed 219 windows but performed
only 21 and 15 aggregate full scans across intermediate jobs. Capacity catch-up took 554.077 seconds
and the complete conflict/resolution gate took 634.194 seconds: 15.3% and 19.5% below ADR 0330's
654.214-second and 788.317-second VM baseline. The run ended with zero staged objects, late-offer
cancellations, retained offer IDs, retirement evictions, or watchdog restarts. Compact proof
`.sandwurm/exports/three-writer/run.yDPmVYg6` independently verifies; its manifest SHA-256 is
`1c758ea9188f4e786d53a9f0743912c52d5e01fc5b6cfff85c43268aa5052b06`.

The differing direct and VM speedups are not contradictory. They show that complete-store hashing
was a real constrained-guest contention amplifier, while other costs dominate the less constrained
host run. The mechanism win is unambiguous in both environments: batch count remains 219 while
complete scan count falls by 90.4%/93.2% in the VM and 96.8%/97.7% direct.

The cache is an optimization, never durable truth. Abrupt exit may leave additional valid unreachable
CAS objects, as before, but cannot expose a branch or projection without the final fence. This does
not defend against storage that lies consistently about reads or `fsync`, does not reserve disk space,
and does not close whole-VM power-cut, long-soak, backup, or precious-data gates. Native filesystem
watching/debounce, incremental source scanning and projection, object bundling, fewer per-object
durability barriers, and route-aware scheduling remain separate measured frontiers.
