# Fixtures

This folder holds **small, reproducible test workspaces and log samples** used to validate proposals and prototypes.

Guidelines:
- Keep fixtures tiny (<200KB total per fixture).
- Prefer deterministic outputs and include expected outputs.
- Include a short README per fixture explaining what it covers.

Current fixture sets:
- `cargo-event-stream/` — samples for “dirty stdout” and mixed human/JSON output.
- `buildscript-ux/` — samples that mimic noisy build.rs failures, hidden warnings, cached build-script JSON, and `cargo::error` edge cases.

- `cargo-global-cache-policy-gc-kit/` — sample Cargo-home inventories, GC plans, and cleanup receipts.
- `doctest-runtool-profile-kit/` — sample target matrices, ignore audits, and doctest runner receipts.
- `debuggability-support-contract-kit/` — symbol-sidecar manifests, support-posture reports, and debugger-ready drift bundles.
- `async-dyn-transition-kit/` — dispatch-recipe ledgers, allocation profiles, and migration receipts for evolving async dyn strategies.
- `borrowsanitizer-workflow-evidence-kit/` — aliasing/provenance finding bundles, FFI boundary maps, and optional Miri comparisons.
- `msrv-workspace-lab/` — MSRV policy files, minimized toolchain matrices, and blame/diff bundles for mixed-workspace support promises.
- `cargo-workspace-boundary-doctor-kit/` — parent-probe traces, ancestor-discovery receipts, config-layering reports, invocation-mode reports, and workspace/config boundary diagnosis bundles.

- `debugger-visualizer-compatibility-kit/` — visualizer compatibility receipts, backend matrices, and tiny render-golden scenarios
