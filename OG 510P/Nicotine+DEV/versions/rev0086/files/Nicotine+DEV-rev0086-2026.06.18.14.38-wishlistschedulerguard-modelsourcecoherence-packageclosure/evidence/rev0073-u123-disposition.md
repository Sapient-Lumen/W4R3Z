# rev0073 U-123 evidence note

The executable source of truth is `tools/probe_rev0073_u123_disposition.py` and its runtime directory.

The gate checks:

```text
- pinned external source ZIP SHA-256 and exact 3.3.x lane ref;
- independent unpatched, selected-minimal, and strict-experiment source roots;
- selected and strict patch application;
- six explicitly classified focused entrypoints across all three states;
- a 32-request burst measurement in all three states;
- source-order invariants and syntax compilation;
- full upstream unit outcome parity for unpatched versus selected-minimal;
- active artifact readability and byte-reduction constraints.
```

Interpret results using `data/rev0073_u123_test_matrix.csv`. Expected failures are evidence only when at least one test actually ran and the observed state matches the declared role.
