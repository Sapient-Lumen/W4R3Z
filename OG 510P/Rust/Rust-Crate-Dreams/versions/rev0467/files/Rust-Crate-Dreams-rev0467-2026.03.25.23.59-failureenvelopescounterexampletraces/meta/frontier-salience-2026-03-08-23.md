# Frontier salience scan — 2026-03-08 (twenty-third pass)

## Main judgment

This pass **did not** add a new top-level proposal.

Instead, it upgraded **P-0058 native-deps-kit** into a more implementation-shaped crate plan by freezing the boundary the archive still needed most in that frontier: **mode and policy truth** for system vs vendored vs override resolution.

## Ranked frontier after this pass

1. **P-0468 Cargo Resolver Explanation Kit**
2. **P-0469 Cargo Rebuild Explanation Kit**
3. **P-0505 Cargo Host/Target Scope Contract Kit**
4. **P-0058 native-deps-kit**
5. **P-0503 Assurance Case Workbench Kit**
6. **P-0504 Linker Lane Contract & Diagnosis Kit**
7. **P-0494 Cargo Compile-Time-Deps Workflow Kit**
8. **P-0486 Debuggability Support Contract Kit**
9. **P-0433 MC/DC Coverage Workbench Kit**
10. **P-0490 Cargo Lock Contention Witness Kit**

## Why P-0058 moved up

Five current facts make it more concrete than before:

- `system-deps` already documents declarative manifest metadata, target-specific deps, fallback names, build-flag overrides, and internal-build env controls.
- Its standardization issue explicitly identifies additive `vendored` features as a real support and policy problem.
- Cargo’s external-tools docs already say build-script results are available in JSON output.
- Cargo config already supports `target.<triple>.<links>` overrides that skip build scripts entirely.
- Current cross-platform discussion makes it clear that a worthy crate should freeze policy truth and support guidance, not promise one universal package-management solution across every OS.

## What changed in the archive

Added:

- `meta/native-vendoring-mode-boundaries-2026-03-08.md`
- `meta/frontier-salience-2026-03-08-23.md`
- `fixtures/native-deps-kit/resolution-mode.lock.schema.json`
- `fixtures/native-deps-kit/vendoring-policy.report.schema.json`
- `fixtures/native-deps-kit/scenarios/feature_unification_forces_vendoring_blocked_by_policy/*`
- `fixtures/native-deps-kit/scenarios/build_internal_env_forces_vendored_mode/*`
- `entries/2026-03-08-146.md`

Updated:

- `proposals/native-deps-kit.md`
- `fixtures/native-deps-kit/README.md`
- `README.md`
- `INDEX.md`
- `meta/known-existing.md`
- `meta/roadmap.md`
- `meta/research-ledger.md`
- `meta/territory-map.md`
- `meta/llm-hygiene.md`

## What should happen next

The best next passes should prefer:

1. freezing `resolution-mode.lock` and `vendoring-policy.report` vocabulary,
2. proving the mode-lock story on one tiny real `*-sys`-like workspace,
3. and keeping this crate separate from buildscript UX, linker-lane diagnosis, and universal package-manager fantasies.

They should **not** drift into:

- another thin pkg-config wrapper,
- another “Cargo doctor” that absorbs every native-build concern,
- or a faux-universal story that pretends Windows/macOS/Linux distro realities are all equivalent.

## Sources

- `system-deps` docs: https://docs.rs/system-deps/latest/system_deps/
- `system-deps` `Config` docs: https://docs.rs/system-deps/latest/system_deps/struct.Config.html
- `system-deps` issue #97: https://github.com/gdesmott/system-deps/issues/97
- Cargo external tools: https://doc.rust-lang.org/cargo/reference/external-tools.html
- Cargo config: https://doc.rust-lang.org/cargo/reference/config.html
- Cargo issue #14948: https://github.com/rust-lang/cargo/issues/14948
- Cross-platform external dependency discussion: https://internals.rust-lang.org/t/external-dependencies-in-crates-and-cross-platform-development/23154
