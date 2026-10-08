# Frontier salience refresh — 2026-03-22 (199)

## Why P-0491 deserved another pass

The archive already had a credible second-pass proposal for **P-0491 Debugger Visualizer Compatibility Kit**:
asset manifests, backend verdicts, activation routes, formatter origins, render goldens, and portable support bundles.
The remaining weak point was not “can we probe another debugger?”
It was **probe-surface and comparison honesty**.

Current official and primary sources make that gap concrete:

1. The 2026 Rust debugging survey says stellar support requires several versions of different debuggers across multiple operating systems, quality visualizers, and resilience against debugger-version and internal-representation drift.
2. The Rust compiler dev guide says Rust supports three major debuggers — GDB, LLDB, and CDB — and that the CDB engine also powers WinDbg, KD, the Microsoft C/C++ extension for VSCode, and part of the Visual Studio debugger.
3. The debugger-visualizers guide says LLDB is not currently supported through the Rust-embedded visualizer lane and instead points toward a separate formatter-bytecode route.
4. LLDB’s `lldb-dap` docs explicitly split responsibilities among LLDB itself, `lldb-dap`, and IDE integrations.
5. Microsoft’s NatVis docs say Visual Studio can load NatVis from several locations with explicit precedence — embedded `.pdb`, loaded project or solution files, VSIX registrations, and user/system visualizer directories — and that embedded `.pdb` NatVis cannot be updated live during a session.
6. GDB’s current pretty-printer guidance recommends versioned package names so multiple library versions can coexist and register printers against the right objfile.
7. The Rust compiler’s own compiletest debuginfo docs still model debugger family and minimum/ignored debugger versions as explicit review axes.

That makes the sharper missing value here less “another visualizer checker” and more a **support-contract layer for probe-surface receipts, comparison-basis receipts, and portable compatibility bundles**.

## Main ranked takeaway

**P-0491 Debugger Visualizer Compatibility Kit** remains a worthy medium-high lane because it can now offer something adjacent crates still do not:

- a `probe-surface.receipt` for *which debugger surface, version, OS class, and delivery route were actually observed*,
- a `comparison-basis.receipt` for *whether two observations are honestly comparable*,
- and a `visualizer-support-bundle.manifest` that keeps policy, assets, activation route, formatter origin, probe surface, comparison basis, backend verdicts, and drift separate.

## Why this beat adjacent ideas this pass

It beat another **P-0486** pass because **P-0486** already owns the broader debuginfo / sidecar / source-material support contract.
The unresolved question here was narrower and more visualizer-specific: *what exact debugger surface was seen, and can two visualizer observations be compared honestly?*

It beat another generic debugger wrapper idea because current primary sources keep the surface split explicit enough that the missing value is a reviewable receipt layer, not one more launcher.

It beat another LLDB-only formatter pass because the cross-backend comparison problem is broader than one formatter subsystem.

## Boundaries to keep sharp

P-0491 should now own:

1. asset inventory,
2. activation-route truth,
3. formatter-origin truth,
4. probe-surface receipts,
5. comparison-basis receipts,
6. backend support verdicts,
7. and portable visualizer-support bundles.

It should not silently become:

- a universal debugger orchestration framework,
- a symbol/source diagnosis lane,
- a whole formatter-pack ecosystem,
- or a general IDE extension layer.
