# nightly_surface_drift_same_fixture

One minimized fixture is analyzed against two compiler / `rustc_public` windows.
The point is to show that the workbench emits a **compatibility diff**, not just raw failing output.

This scenario should remain distinct from:
- `rustc_public` publication mechanics,
- formal semantics drift,
- and generic release-history diffing.
