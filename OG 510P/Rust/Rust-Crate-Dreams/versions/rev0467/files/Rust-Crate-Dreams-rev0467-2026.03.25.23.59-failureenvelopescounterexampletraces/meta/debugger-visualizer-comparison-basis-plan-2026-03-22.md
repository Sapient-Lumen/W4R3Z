# Debugger Visualizer Compatibility Kit — probe surface and comparison-basis plan (2026-03-22)

Purpose: sharpen **P-0491 Debugger Visualizer Compatibility Kit** into a more implementation-ready support-contract lane.

The archive already had asset manifests, backend matrices, activation routes, formatter-origin receipts, render goldens, and portable support bundles.
The remaining weak spot was comparability.
Current sources now make it clear that “visualizer worked” is not one dimension:

- GDB, LLDB, and CDB are distinct debugger families.
- The CDB engine can appear through WinDbg, KD, VSCode’s C/C++ extension, and part of Visual Studio.
- LLDB can appear through `lldb` CLI or through `lldb-dap` plus an IDE integration.
- NatVis can be delivered from embedded `.pdb` state, project files, VSIX registration, or user/system visualizer folders with explicit precedence.
- GDB pretty-printer loading and version coexistence depend on objfile registration and versioned package naming.

That means a visualizer-compat crate should add two more first-class artifacts.

## 1. `probe-surface.receipt`

This receipt should answer:

- which debugger family and frontend surface were actually observed,
- which version and host OS class applied,
- which delivery container or precedence route carried the active visualizer asset,
- whether the lane was CLI, DAP, IDE-backed, wrapper-backed, or manual-review-only,
- and whether live asset reload or hot-swap was expected.

Suggested fields:

- `backend_family`
- `frontend_surface`
- `debugger_version`
- `host_os_class`
- `delivery_container`
- `delivery_precedence_notes`
- `hot_reload_support`
- `observation_commands`
- `manual_review_required`
- `notes`

## 2. `comparison-basis.receipt`

This receipt should answer:

- whether two observations are comparable,
- which dimensions match or drift,
- whether a difference is a backend-engine change, a frontend-surface change, a delivery-route change, or a formatter-origin change,
- and whether a change should be read as compatibility drift, observation-surface drift, or non-comparable evidence.

Suggested fields:

- `lhs_probe`
- `rhs_probe`
- `comparability`
- `matching_dimensions`
- `drift_dimensions`
- `manual_review_reasons`
- `classification`
- `notes`

Recommended `comparability` vocabulary:

- `comparable`
- `partially_comparable`
- `not_comparable`

Recommended `classification` vocabulary:

- `same_surface`
- `frontend_surface_drift`
- `delivery_route_drift`
- `formatter_origin_drift`
- `backend_version_drift`
- `non_comparable`

## 3. Bundle update

`visualizer-support-bundle.manifest` should now allow:

- `probe_surface_receipt`
- `comparison_basis_receipt`

This lets one portable bundle say not only what assets and backend verdicts exist, but also what surface was observed and whether two receipts can be compared honestly.

## Scenario families to add

1. **NatVis embedded in `.pdb` is not the same observation surface as a solution-loaded `.natvis` file.**
2. **`lldb-dap` plus IDE integration is not silently interchangeable with `lldb` CLI.**
3. **GDB versioned pretty-printer package drift is comparison-basis drift, not necessarily plain asset failure.**
4. **Portable bundles keep surface and comparison receipts separate from origin and backend verdicts.**

## MVP implementation sequence

1. Extend asset capture with a conservative delivery-container classifier.
2. Emit `probe-surface.receipt` before running any broad probe matrix.
3. Emit `comparison-basis.receipt` only when two observations are compared.
4. Keep `manual_review_required` prominent whenever delivery precedence or frontend layering is inferred rather than observed.
5. Reuse existing backend verdicts and formatter-origin receipts rather than duplicating them.

## Receiver-facing value

Another engineer should be able to read one portable bundle and answer:

- what debugger surface was actually tested,
- whether the result depended on embedded or external asset delivery,
- whether the observation came through CLI, DAP, or IDE layers,
- whether comparison against another release is honest,
- and whether any apparent regression is really asset drift or only observation-surface drift.

## Boundaries

This lane should remain distinct from:

- **P-0486** broad debuggability posture,
- **P-0493** source-path / source-material lookup,
- **P-0083** broad formatter-pack ambition.

**P-0491** should own visualizer asset compatibility and comparison honesty above the documented debugger surfaces.
