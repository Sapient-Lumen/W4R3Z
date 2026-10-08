# Scenario family — docs.rs-specific cfg or rustc args expose a documentation slice

This fixture family exists for crates whose documentation surface depends on docs.rs-specific assumptions.

It is meant to catch support drift such as:

- `#[cfg(docsrs)]` changes what the final crate shows in hosted docs,
- docs.rs metadata injects a custom cfg or feature that normal users do not get,
- dependencies do not see the same `docsrs` cfg even though the top-level crate does,
- and a maintainer starts speaking as if the hosted docs slice were an ordinary dependency slice.

A good availability ledger should make four things explicit:

1. whether the origin includes **`docsrs_cfg`** or **`docsrs_rustc_arg`**,
2. whether the slice is classed as **`docsrs_assumed_only`**,
3. whether the fidelity comes from hosted import versus direct local observation,
4. and whether doctor mode raises `docsrs_only_final_crate_scope_mismatch`.
