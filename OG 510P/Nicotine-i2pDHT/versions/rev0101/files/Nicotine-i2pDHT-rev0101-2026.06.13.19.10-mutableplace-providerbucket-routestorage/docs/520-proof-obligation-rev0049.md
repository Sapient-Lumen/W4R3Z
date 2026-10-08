# Proof obligation rev0049

Before a public edge write is allowed in a future prototype, the implementation should be able to show:

1. bridge-shadow, audit-quorum, redress-GC, and optional transport-shadow digests bind to the same side-effect scope;
2. watch components do not silently become unwatched writes;
3. witness compaction keeps live refutations, fork evidence, and redress gaps;
4. restart memory keeps required component digests and hard-negative facts;
5. sequence and previous-digest memory reject replay, rollback, and fork.
