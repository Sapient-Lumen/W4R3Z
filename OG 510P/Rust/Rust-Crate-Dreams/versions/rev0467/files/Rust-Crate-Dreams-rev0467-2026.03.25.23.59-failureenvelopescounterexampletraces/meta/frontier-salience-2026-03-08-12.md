# Frontier salience scan — 2026-03-08 (twelfth pass)

## Main judgment

This pass again did **not** add another top-level proposal.

Instead, it made **P-0489 Cargo Build-Dir Consumer Transition Kit** more implementation-ready.
The upstream Cargo story is now explicit enough that the archive should stop treating build-dir migration as a vague future concern.
The missing layer is a **portable transition bundle** above stable `build.build-dir`, unstable layout work, existing build-script/env surfaces, and Cargo JSON output.

## Ranked frontier after this pass

1. **P-0469 Cargo Rebuild Explanation Kit**
2. **P-0468 Cargo Resolver Explanation Kit**
3. **P-0494 Cargo Compile-Time-Deps Workflow Kit**
4. **P-0490 Cargo Lock Contention Witness Kit**
5. **P-0046 buildscript-ux-kit**
6. **P-0486 Debuggability Support Contract Kit**
7. **P-0035 cargo-build-insights**
8. **P-0489 Cargo Build-Dir Consumer Transition Kit**
9. **P-0059 buildscript-testkit**
10. **P-0058 native-deps-kit**

## Why P-0489 improved

Six current facts matter here:

- Cargo build-cache docs now clearly split final artifacts from intermediate artifacts and say the build-dir layout is internal.
- Cargo config docs make `build.build-dir` stable enough that more users and tools will actually exercise alternative layouts.
- Release notes now warn that tools depending on internal build-dir details may break and explicitly ask people to test these cases.
- Cargo project-goal docs say tooling that accesses intermediate artifacts needs a transition path.
- External-tools JSON plus build-script/env docs already expose several narrower safer surfaces.
- rust-analyzer is already discussing `build-dir` support, showing that downstream consumers are adapting rather than staying hypothetical.

That means **P-0489** does not need to invent a new Cargo API or a cache manager.
It can be precise about its 0.1 contract:

- one consumer inventory,
- one layout snapshot,
- one consumer audit,
- one path contract,
- one adapter plan,
- one transition receipt,
- optionally one diff,
- and one compact notes file.

## What should happen next

The best next passes on this frontier should prefer:

1. scenario bundles for `deps/` scraping, build-script-output scraping, old-vs-new layout rehearsals, and artifact-handoff redirects,
2. vocabulary alignment across **P-0494 / P-0490 / P-0489**,
3. conservative provenance and evidence-strength fields,
4. and redaction rules strong enough for real support bundles.

They should **not** add another generic “Cargo output migration” idea unless it is clearly distinct from:

- parity / fallback artifacts,
- live blocking witnesses,
- final-artifact handoff,
- or build-dir consumer migration.

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
