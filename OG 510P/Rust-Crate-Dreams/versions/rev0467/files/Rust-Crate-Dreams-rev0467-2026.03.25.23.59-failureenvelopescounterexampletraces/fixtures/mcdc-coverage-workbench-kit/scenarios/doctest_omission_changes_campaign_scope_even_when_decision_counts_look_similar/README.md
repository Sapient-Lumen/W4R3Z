# Scenario — doctest omission changes campaign scope even when decision counts look similar

This scenario protects the distinction between **similar-looking totals** and **the same campaign scope**.

The rustc coverage book documents that including doctests requires dropping `--tests` and using unstable doctest persistence flags, while `cargo-llvm-cov` also documents doctest support as unstable.
A bundle that omitted doctests therefore needs an explicit `campaign-scope.receipt.json` instead of pretending to be directly comparable to a later bundle that included them.
