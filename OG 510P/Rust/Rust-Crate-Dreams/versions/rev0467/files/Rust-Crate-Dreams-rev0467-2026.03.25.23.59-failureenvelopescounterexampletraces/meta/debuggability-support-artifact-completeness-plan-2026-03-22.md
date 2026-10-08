# Debuggability support artifact-completeness plan — 2026-03-22

This note deepens **P-0486 Debuggability Support Contract Kit** around one product question:

> what exact artifacts should another engineer receive when a build is described as “debuggable” so support posture, checked backends, source lookup, and handoff stay reviewable instead of collapsing into one vague claim?

## Product stance

The crate should stay **reviewer-facing, read-first, and conservative**.
It should not become:

- a debugger frontend,
- an IDE integration layer,
- a symbol server,
- or a source-packaging system that hides review boundaries.

Its job is to emit a compact pack that answers:

- what broad debuggability posture a build honestly has,
- which debugger family / OS / version / capability lane was actually observed,
- what source material is needed for lookup after path hygiene or remapping,
- which symbol sidecars or visualizer assets are required for the promise,
- how those truths changed across revisions,
- and what still needs manual review.

## New first-class artifacts

### `backend-observation.receipt.json`

Record exact debugger-lane observations without pretending artifact presence equals broad backend support.

For each observation, record:

- backend family,
- backend version,
- operating system / target,
- evidence kind (`interactive_session`, `artifact_inference_only`, `imported_report`, `manual_review_required`),
- capability classes checked,
- capability classes left unchecked,
- verdict (`observed_working`, `observed_partial`, `artifact_inference_only`, `manual_review_required`),
- notes on portable-claim ceilings.

This keeps “PDB exists” separate from “LLDB also supports Rust expression evaluation here”.

### `source-material.manifest.json`

Record what source inputs are needed for human or tool-driven lookup once debug paths have been trimmed, remapped, or externalized.

For each material entry, record:

- logical name,
- material kind (`workspace_source_tree`, `source_archive`, `sysroot_sources`, `generated_source_bundle`, ...),
- location class,
- lookup role,
- share posture,
- remapped-prefix hints,
- notes on whether the material is omitted, redacted, or required only for internal debugging.

This keeps “path hygiene improved” separate from “source lookup is still reviewable”.

### `debug-support-bundle.manifest.json`

The portable thing another reviewer opens first.

For one exported pack, record:

- subject,
- broad support posture,
- artifact list,
- which artifacts are required for review,
- share posture,
- manual-review gaps,
- and notes on whether the bundle includes source material directly or only references it.

This keeps “we zipped the binaries” separate from “we exported an honest debugger-support bundle”.

## CLI / workflow refinement

### `capture`
Existing capture flow should now be able to emit broad posture plus optional backend-observation receipts and source-material manifests.

### `doctor`
Should render warnings such as:

- `backend_checked_only_for_visual_studio_family`
- `artifact_rich_build_still_lacks_async_debug_evidence`
- `trimmed_paths_need_internal_source_material_reference`
- `bundle_missing_required_sidecar_for_promised_posture`
- `share_posture_conflicts_with_source_material_inclusion`

### `pack`
Should emit one `debug-support-bundle.manifest.json` plus the underlying receipts/manifests/reports rather than assuming copied binaries are self-explanatory.

## Receiver-facing value

### For release engineers
Know which symbol sidecars, visualizer assets, and optional source materials must be preserved for the promised support posture.

### For support engineers
Receive one bundle that distinguishes artifact presence, actual debugger-lane evidence, and source-lookup requirements.

### For privacy/security reviewers
See exactly what source material is required for lookup and whether that material is safe to share externally.

### For downstream integrators
Avoid over-reading one backend observation into a universal support promise.

## Good first scenario families

1. **Windows MSVC build has PDB + NatVis and works in one checked Visual Studio lane, but LLDB / async / Rust-expression claims remain unchecked.**
2. **`trim-paths` or remapping keeps source paths private, but an internal source archive is still required for practical lookup.**
3. **A portable review bundle must keep posture, sidecars, backend observations, and source materials separate instead of assuming copied final artifacts are enough.**

## Boundary reminders

Keep **P-0486** separate from:

- **P-0491** visualizer conformance work,
- **P-0493** source-path / lookup diagnosis,
- **P-0101** crash-artifact and symbolication workflows,
- and generic debugger UX or IDE integration work.

The missing value here is the **joined debuggability support artifact** above Cargo / rustc / debugger substrate and below any broader debugger product.

## Sources

- https://blog.rust-lang.org/2026/02/23/rust-debugging-survey-2026/
- https://blog.rust-lang.org/2026/03/20/rust-challenges/
- https://doc.rust-lang.org/cargo/reference/profiles.html
- https://doc.rust-lang.org/rustc/codegen-options/index.html
- https://doc.rust-lang.org/reference/attributes/debugger.html
- https://doc.rust-lang.org/cargo/reference/build-cache.html
- https://blog.rust-lang.org/2026/03/13/call-for-testing-build-dir-layout-v2/
