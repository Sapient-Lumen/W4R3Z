# Doctest Extraction & Support Contract Kit — product plan (2026-03-22)

Proposal: **P-0455 Doctest Extraction & Support Contract Kit**

## Product thesis

Rust now has enough doctest substrate that a maintainers-facing support layer becomes plausible:
- docs remain the preferred canonical reference for Rust users;
- rustdoc can emit machine-readable doctest extraction output on nightly;
- rustdoc has stable runtool support for wrappers like QEMU/VMs;
- target-specific ignore annotations are now explicit;
- grouping/merged-doctest behavior is a real execution mode.

The missing product is therefore a crate and cargo-adjacent tool that make documentation-example posture inspectable by **other people**.

## v0.1 product shape

### Core artifacts

- `doctest.manifest.json`
  - extracted cases, source spans, block attributes, item paths, and extraction provenance
- `extraction-basis.receipt.json`
  - extraction authority, toolchain/version, format version, and notes on how much came from first-party rustdoc output versus downstream reconstruction
- `rewrite-lineage.receipt.json`
  - post-extraction harness injections, environment shims, hidden setup expansion notes, and rationale
- `execution-mode.receipt.json`
  - standalone vs merged vs compile-only vs ignored vs wrapper-executed posture, plus runner/grouping basis
- `docs-example-support.report.json`
  - per-example support class across host run, target run, compile-only, render-only, ignored, or manual-review lanes
- `grouping-comparison.report.json`
  - compares two bundles and classifies basis/grouping/target/attribute comparability
- `docs-example-drift.diff.json`
  - compares two bundles and classifies support shifts, rewrite shifts, and grouping shifts
- `doctest-support-bundle.manifest.json`
  - compact manifest for handoff, imports, redactions, and review-safe summaries

### Command surface

- `cargo doctest-contract extract`
  - capture the manifest and optional extracted files
- `cargo doctest-contract check`
  - emit execution-mode and support reports without requiring a giant CI wrapper
- `cargo doctest-contract diff <old> <new>`
  - compare docs-example posture across branches/toolchains/targets
- `cargo doctest-contract bundle`
  - emit a small shareable support bundle for CI or issue filing

## What the crate should provide other people

1. **A boring machine-readable inventory** of documentation examples.
2. **Explicit rewrite honesty** when custom environments modify examples after extraction.
3. **Execution-basis honesty** when the meaning of “the example ran” depends on grouping or wrappers.
4. **Support-class honesty** across host execution, target execution, compile-only posture, ignore posture, and docs.rs rendering.
5. **Comparability honesty** when basis/grouping drift makes trend claims unsafe.
6. **Diffable review artifacts** for policy drift and toolchain drift.

## Intended users

- docs-heavy library maintainers
- embedded / kernel / cross-target teams with special runner needs
- release engineers who gate documentation posture
- rustdoc contributors collecting reduced evidence for regressions
- downstream integrators who need to know whether example support is real or aspirational

## Design axioms

1. **Manifest first** — extraction should be inspectable before execution.
2. **Rewrite explicit** — environment-specific modifications must be recorded.
3. **Execution mode visible** — standalone, merged, wrapper, and compile-only remain distinct.
4. **Support class conservative** — render-only/docs.rs success never masquerades as execution.
5. **Interop with adjacent lanes** — runner profile, hosted parity, and coverage work should compose, not collapse.

## Adjacent-lane boundaries

- Reuse **P-0481** for target/emulator runner profiles.
- Reuse **P-0472** for docs.rs hosted parity.
- Reuse **P-0476** for coverage / public-doc debt review.
- Reuse **P-0451** for item availability / `cfg` visibility truth.

## MVP fixture families

1. hidden setup + custom harness rewrite lineage
2. nightly JSON extraction basis versus Markdown fallback authority
3. merged vs standalone execution mode changes
4. host run vs cross compile vs docs.rs render support-class separation
5. ignore-target or runner-policy changes producing drift

## Adoption path

1. stabilize the schemas first
2. ship manifest-only mode before ambitious runners
3. import existing rustdoc/Cargo output conservatively
4. make basis/comparison receipts good enough for PR review before adding more execution backends
