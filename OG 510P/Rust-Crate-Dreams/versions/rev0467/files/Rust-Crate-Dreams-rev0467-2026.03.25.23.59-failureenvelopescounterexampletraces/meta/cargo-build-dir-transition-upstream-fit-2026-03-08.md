# Cargo build-dir consumer transition upstream fit — 2026-03-08

## Main judgment

**P-0489 Cargo Build-Dir Consumer Transition Kit** is now a much clearer fit to current upstream Cargo reality than it was when first proposed.

The reason is not that upstream finished the transition.
The reason is that upstream now makes the **substrate and warning signs** unusually explicit:

- Cargo’s build-cache docs now clearly split final artifacts from intermediate artifacts and say the build-dir layout is internal.
- Cargo config docs make `build.build-dir` a stable user-facing surface.
- Release notes now warn that tools relying on build-dir internals may break for users changing layout and explicitly recommend proactive testing.
- Nightly Cargo has `-Zbuild-dir-new-layout` and Cargo’s project goals say tooling that accesses intermediate artifacts needs a transition path.
- Cargo’s external-tools JSON already exposes produced artifacts and build-script execution data.
- Build-script and environment-variable docs already document narrower safer surfaces like `OUT_DIR` and `CARGO_BIN_EXE_<name>`.
- rust-analyzer is already discussing build-dir support, which is further evidence that downstream tools are adapting to a moving build-dir story.

That means **P-0489** no longer needs to act like it is proving Cargo internals might change someday.
It should instead standardize the **receiver-facing migration bundle** above that substrate.

## What the crate should not try to own

### Not P-0494
**P-0494** is about what a tool-oriented workflow actually built and when it should fall back.
A build-dir transition kit may mention tool workflows as consumers, but it should not become a general parity checker.

### Not P-0490
**P-0490** is about live waits and who blocked whom.
A build-dir transition kit may mention shared roots, but it should not become a live lock-contention witness.

### Not P-0471
**P-0471** is about handing off final produced artifacts.
P-0489 should sometimes route consumers *toward* that handoff, but it should remain focused on transitional consumers that still touch intermediate layout.

### Not a new Cargo public API proposal in disguise
The crate should not pretend it can “stabilize Cargo internals from the outside.”
Its job is to inventory assumptions, route to better surfaces when possible, and preserve `manual_review_required` when no safe contract exists yet.

## Strongest current 0.1 artifact contract

The sharpest 0.1 shape now looks like:

1. one `consumer-inventory.manifest.json`,
2. one `layout.snapshot.json`,
3. one `consumer-audit.report.json`,
4. one `path-contract.json`,
5. one `adapter-plan.json`,
6. one `transition.receipt.json`,
7. optionally one `transition.diff.json`,
8. and one short `notes.md`.

That is enough to answer:

- which consumers still rely on internal layout,
- how that was observed,
- which safer surface already exists,
- and whether the migration is safe, risky, or still blocked on upstream.

## Best existing adapter substrate to reuse

The proposal should reuse existing Cargo surfaces before inventing new ones:

- `OUT_DIR` for build-script-owned outputs,
- `build-script-executed` JSON for parsed build-script results,
- `CARGO_BIN_EXE_<name>` when the real need is an integration-test-visible binary path,
- dep-info when the real need is external-build-system dependency tracking,
- and final-artifact handoff patterns when the consumer should stop touching intermediate layout altogether.

## Why this is better than another generic Cargo tooling crate

The official docs now expose enough of the shape of the problem that another vague “Cargo tooling migration helper” would be too fuzzy.
A worthy crate here should hand maintainers one small honest bundle they can attach to a PR, support issue, or upgrade rehearsal.

## Best next repo moves

Future passes on this frontier should prefer:

1. scenario bundles for `deps/` scraping, `build/` scraping, old-vs-new layout rehearsals, and artifact-handoff redirects,
2. schema stabilization for `observed_from`, `evidence_strength`, `manual_review_required`, and `blocked_on_upstream`,
3. explicit redaction rules for local paths and proprietary helper names,
4. and more examples of adapter routing to already-existing Cargo surfaces.

They should not add another generic “Cargo output tooling” proposal unless it is clearly distinct from:

- final-artifact handoff,
- tool-build parity,
- live lock contention,
- or build-dir consumer transition.

## Sources

- Cargo build-cache docs: https://doc.rust-lang.org/cargo/reference/build-cache.html
- Cargo config docs: https://doc.rust-lang.org/cargo/reference/config.html
- Cargo external-tools docs: https://doc.rust-lang.org/cargo/reference/external-tools.html
- Cargo build-script docs: https://doc.rust-lang.org/cargo/reference/build-scripts.html
- Cargo environment variables docs: https://doc.rust-lang.org/cargo/reference/environment-variables.html
- Rust release notes: https://doc.rust-lang.org/beta/releases.html
- Cargo unstable docs (`build-dir-new-layout`): https://doc.rust-lang.org/cargo/reference/unstable.html#build-dir-new-layout
- Cargo build-dir layout goal: https://rust-lang.github.io/rust-project-goals/2025h2/cargo-build-dir-layout.html
- User-wide build cache goal: https://rust-lang.github.io/rust-project-goals/2024h2/user-wide-cache.html
- rust-analyzer `build-dir` support issue: https://github.com/rust-lang/rust-analyzer/issues/20150
