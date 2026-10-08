# Successor-safe ceremony receipt package supersession records should collapse to compact lineage records

Once the archive has more than one package supersession record, pairwise replacement artifacts stop being enough.

A future steward still has to answer three questions cheaply:

1. Which package manifest is authoritative right now?
2. Which older package roots did it replace, in order?
3. Did the active receipt locator stay stable across that chain or rotate at some point?

A compact package lineage record answers those questions without copying any package bodies. It should name the authoritative head manifest, the ordered manifest chain, the ordered supersession chain, the locator-continuity result across the whole line, and the current review/advisory basis that keeps the head authoritative.

That is tighter than a prose changelog and safer than local filename browsing. It lets the inheritor validate the current package root from one tiny object while still keeping the older package states available for audit.

## Local implementation move

This archive now ships a machine-checkable package-lineage schema, tool command, worked snapshot, and checker coverage for the successor-safe ceremony receipt package lane.

The worked lineage snapshot is intentionally small: two manifests, one supersession record, one authoritative head, and one locator-continuity result. The point is not to retain more history prose; it is to keep the minimum machine-checkable object that says how authority flowed across package refreshes.
