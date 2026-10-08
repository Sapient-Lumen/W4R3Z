# Frontier salience refresh — 2026-03-22 (198)

## Why P-0481 deserved another pass

The archive already had a credible first-pass proposal for **P-0481 Doctest Runtool Profile Kit**:
runner profiles, target matrices, ignore audits, results, receipts, and bundle exports.
The remaining weak point was not “can we run doctests under QEMU?”
It was **route and basis honesty**.

Current official and primary sources make that gap concrete:

1. The rustdoc command-line docs now make `--test-runtool` and `--test-runtool-arg` explicit, including wrapper argument order and the fact that the doctest executable path is passed after wrapper args.
2. Cargo’s current unstable-features docs say doctest cross-compilation is unconditionally enabled starting in Rust 1.89 and that doctests now honor `--target`.
3. Current release notes keep cross-target doctests, target-specific `ignore-*`, and stable runtool flags in the official substrate at the same time.
4. Cargo’s config docs keep `target.<triple>.runner`, `target.<cfg>.runner`, and `CARGO_TARGET_<triple>_RUNNER` real execution routes with explicit precedence.
5. Cargo’s `cargo test` docs still warn that the doctest execution model is not guaranteed and may change.
6. Those docs also keep an important path fact explicit: doctest compilation happens with `rustdoc` invoked from the workspace root, but each doctest runs with the package root as working directory via `--test-run-directory`.
7. Rust-for-Linux’s tooling goal still asks for stable extraction/customization of doctests for special environments.
8. rustdoc’s `--persist-doctests` support remains unstable, so persisted binaries are useful imports rather than the stable contract itself.

That makes the sharper missing value here less “another emulator recipe” and more a **support-contract layer for runner-route provenance, execution basis, and portable handoff bundles**.

## Main ranked takeaway

**P-0481 Doctest Runtool Profile Kit** remains a worthy medium-high lane because it can now offer something adjacent crates still do not:

- a `runner-route.receipt` for *how the effective runner was actually selected*,
- an `execution-basis.receipt` for *what target/support/working-directory/ignore policy was actually in force*,
- and a `doctest-runtool-support-bundle.manifest` that keeps route, basis, results, and imports separate.

## Why this beat adjacent ideas this pass

It beat another **P-0455** pass because **P-0455** now already owns extraction-basis and grouping-comparison truth.
The unresolved question here was more operational and more review-critical: *how did the executable actually get wrapped, and what execution basis did that target lane really have?*

It beat another **P-0472** docs.rs parity pass because hosted docs surface is not the same as special-environment doctest execution.

It beat another generic emulator-framework idea because the missing value is narrower and more reviewable: a conservative bundle that can explain one route and one basis honestly.

## Boundaries to keep sharp

P-0481 should now own:

1. runner-route provenance,
2. target/emulator runner-profile policy,
3. target-specific ignore audit posture,
4. compile-vs-run directory basis,
5. execution support class,
6. route/basis drift,
7. and portable runtool-support bundles.

It should not silently become:

- a generic emulator orchestration framework,
- a hosted docs reproducer,
- a general-purpose cross-device test harness,
- or a substitute for extraction-basis work in **P-0455**.
