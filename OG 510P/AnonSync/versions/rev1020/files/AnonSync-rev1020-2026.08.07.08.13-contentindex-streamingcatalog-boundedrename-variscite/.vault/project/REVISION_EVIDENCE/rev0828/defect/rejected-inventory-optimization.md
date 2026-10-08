# Rejected inventory-audit optimization

During the full gate, multiple stale rev0828 worktrees were discovered launching
old CTest processes concurrently. Before that process interference was isolated,
a line-number lookup in `tools/rev0763_persistence_boundary_audit.py` was
suspected of causing quadratic behavior.

A preindexed-newline variant and an incremental variant were benchmarked against
the unchanged implementation. At this repository size the proposed preindexed
variant was slightly slower, and no reliable sealed-source speedup was shown.
Both experimental variants were discarded. The active source in rev0828 is
byte-identical to the parent for this audit.

This evidence is retained because rejecting an attractive but unsupported
optimization is part of the audit result. No performance improvement is claimed.
