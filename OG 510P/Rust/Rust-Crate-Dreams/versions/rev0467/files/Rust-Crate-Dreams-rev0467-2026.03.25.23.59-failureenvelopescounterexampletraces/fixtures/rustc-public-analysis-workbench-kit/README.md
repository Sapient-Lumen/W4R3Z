# rustc_public Analysis Workbench Kit fixtures

These fixtures are for **P-0429 rustc_public Analysis Workbench Kit**.

The point is to freeze the layer above `rustc_public`:

- compiler / `rustc_public` compatibility locks,
- minimized analyzer fixtures,
- tool capability matrices,
- analysis receipts,
- and semver-exempt surface quarantine reports.

These fixtures should stay distinct from:

- `rustc_public` publication / release engineering itself,
- `rustc_private` migration shims,
- formal semantics / counterexample bridges,
- and Rust specification witnesses.

Scenario families in this pass:
- `nightly_surface_drift_same_fixture/`
- `unstable_module_leak_quarantine/`
- `cross_tool_async_capability_gap/`
