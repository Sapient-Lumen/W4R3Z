# Frontier salience scan — 2026-03-08 (twenty-fourth pass)

## Main judgment

This pass again did **not** add a new top-level proposal.

Instead, it upgraded **P-0496 Cargo Vendor & Source Parity Kit** into a more implementation-shaped crate plan by freezing the boundary the archive still needed most in that frontier: **source identity and coverage truth** for vendored/source-replaced builds.

## Ranked frontier after this pass

1. **P-0468 Cargo Resolver Explanation Kit**
2. **P-0469 Cargo Rebuild Explanation Kit**
3. **P-0496 Cargo Vendor & Source Parity Kit**
4. **P-0505 Cargo Host/Target Scope Contract Kit**
5. **P-0058 native-deps-kit**
6. **P-0503 Assurance Case Workbench Kit**
7. **P-0504 Linker Lane Contract & Diagnosis Kit**
8. **P-0494 Cargo Compile-Time-Deps Workflow Kit**
9. **P-0486 Debuggability Support Contract Kit**
10. **P-0490 Cargo Lock Contention Witness Kit**

## Why P-0496 moved up

Six current facts make it more concrete than before:

- Cargo source replacement explicitly assumes the replacement source contains the **exact same source code** and no extra crates.
- Cargo says source replacement is **not** the tool for patching or private-registry semantics.
- `cargo vendor` already exposes workflow-specific flags like `--sync`, `--respect-source-config`, and `--versioned-dirs`.
- Cargo’s offline docs warn that offline mode may yield **different dependency resolution** than online mode.
- Cargo still has open issues where multiple replaced sources routed into one vendored directory do not behave like one clean identity lane.
- Cargo still has open gaps around replaced git sources needing git-style history and around vendoring path dependencies.

That means **P-0496** does not need to invent another mirror.
It can be precise about a 0.1 contract:

- one source-origin receipt,
- one source-parity lock,
- one coverage report,
- one conservative parity verdict,
- and one diff for comparing environments.

## What changed in the archive

Added:

- `meta/cargo-source-parity-boundaries-2026-03-08.md`
- `meta/frontier-salience-2026-03-08-24.md`
- `fixtures/cargo-vendor-source-parity-kit/source-parity.lock.schema.json`
- `fixtures/cargo-vendor-source-parity-kit/source-coverage.report.schema.json`
- `fixtures/cargo-vendor-source-parity-kit/scenarios/multi_registry_alias_split/*`
- `fixtures/cargo-vendor-source-parity-kit/scenarios/git_workspace_history_required/*`
- `fixtures/cargo-vendor-source-parity-kit/scenarios/path_dependency_outside_vendor_boundary/*`
- `entries/2026-03-08-147.md`

Updated:

- `proposals/cargo-vendor-source-parity-kit.md`
- `fixtures/cargo-vendor-source-parity-kit/README.md`
- `fixtures/cargo-vendor-source-parity-kit/source-origin.receipt.schema.json`
- `README.md`
- `INDEX.md`
- `meta/known-existing.md`
- `meta/roadmap.md`
- `meta/research-ledger.md`
- `meta/prioritization.md`
- `meta/territory-map.md`
- `meta/llm-hygiene.md`

## What should happen next

The best next passes should prefer:

1. freezing `source-parity.lock` and `source-coverage.report` vocabulary,
2. proving the bundle on one tiny real multi-source or vendor-heavy workspace,
3. and keeping this crate separate from mirrors, package review, and air-gap transfer tooling.

They should **not** drift into:

- another generic “offline Cargo doctor”,
- another registry or mirror implementation,
- or a faux-universal hermeticity prover that overclaims what Cargo’s current surfaces can justify.

## Sources

- Cargo source replacement: https://doc.rust-lang.org/cargo/reference/source-replacement.html
- `cargo vendor`: https://doc.rust-lang.org/cargo/commands/cargo-vendor.html
- `cargo fetch`: https://doc.rust-lang.org/cargo/commands/cargo-fetch.html
- Cargo dependency overrides: https://doc.rust-lang.org/cargo/reference/overriding-dependencies.html
- Cargo changelog: https://doc.rust-lang.org/cargo/CHANGELOG.html
- Cargo issue #14821: https://github.com/rust-lang/cargo/issues/14821
- Cargo issue #16141: https://github.com/rust-lang/cargo/issues/16141
- Cargo issue #10134: https://github.com/rust-lang/cargo/issues/10134
