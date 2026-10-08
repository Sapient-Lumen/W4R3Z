# Linker Lane Contract Kit fixtures

This fixture family is for **linker-lane contracts, diagnosis reports, and lane-switch diffs**.

The point is not to benchmark every linker.
The point is to make linker assumptions **portable and reviewable**.

## Suggested scenario corpus

1. `linux_system_default_vs_self_contained_lld/`
   - same target, different linker lane
   - should classify whether the shift is performance-only or support-surface-changing

2. `host_flag_leakage_without_explicit_target/`
   - global `RUSTFLAGS` / `build.rustflags` affect host tools unexpectedly
   - should produce `host_flag_leakage` or `driver_flag_scope_mismatch`

3. `windows_msvc_from_linux_xwin_lane/`
   - Windows MSVC target from a non-Windows host
   - should capture SDK/CRT provenance and runner caveats

4. `zig_lane_with_glibc_floor/`
   - Zig-backed GNU target with an explicit glibc floor
   - should preserve the lane’s external assumptions and target suffix facts

5. `containerized_cross_lane/`
   - build succeeds only in the containerized lane
   - should surface container dependence rather than pretending the host is equivalent

## First schema targets

- `linker-lane.manifest.json`
- `link-diagnosis.report.json`
- optional later: `lane-switch.diff.json`, `support-risk.report.json`
