# Patch-composition authority — rev0085

A clean candidate application to the bundled proxy does not prove that the
candidate and a later public delta compose safely. Rev0085 makes composition a
machine contract rather than a prose assumption.

The audit verifies:

- current public-head and candidate artifact IDs and digests;
- exact target-path sets;
- zero target-path overlap;
- `git apply --check`, apply, and reverse-check evidence in both orders;
- byte-identical final tree inventories;
- a pinned expected composed-tree identity; and
- five negative-control mutations.

The current relationship is `disjoint-commutative`. A future overlapping public
change must fail this contract and trigger a candidate rebase or retirement;
path disjointness is never inherited across revisions.
