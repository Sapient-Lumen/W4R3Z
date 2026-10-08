# Frontier salience scan — 2026-03-08 (twenty-first pass)

## Main judgment

This pass **did not** add a new top-level proposal.

Instead, it promoted **P-0505 Cargo Host/Target Scope Contract Kit** from “good frontier note” to a more implementation-shaped target with concrete schemas and scenario bundles.

## Ranked frontier after this pass

1. **P-0469 Cargo Rebuild Explanation Kit**
2. **P-0468 Cargo Resolver Explanation Kit**
3. **P-0505 Cargo Host/Target Scope Contract Kit**
4. **P-0503 Assurance Case Workbench Kit**
5. **P-0504 Linker Lane Contract & Diagnosis Kit**
6. **P-0494 Cargo Compile-Time-Deps Workflow Kit**
7. **P-0486 Debuggability Support Contract Kit**
8. **P-0433 MC/DC Coverage Workbench Kit**
9. **P-0453 Safety Contract Consumer Kit**
10. **P-0490 Cargo Lock Contention Witness Kit**

## Why P-0505 moved up

Five current facts make it more concrete:

- Cargo’s stable config docs explicitly document that `RUSTFLAGS` / `build.rustflags` apply to all compiler invocations without `--target`, but only to the target when `--target` (or `build.target`) is used.
- Cargo’s config docs separately document `build.rustdocflags` and `target.*.rustdocflags`, which means rustdoc belongs in the same scope family rather than being treated as an unrelated edge case.
- Cargo’s unstable docs still describe `target-applies-to-host` and `[host]` as unstable features, and say that `target-applies-to-host` may default to `false` in the future.
- The tracking issues for `target-applies-to-host` and `host-config` are still open and marked as waiting on feedback / unstable baking.
- Cargo’s internal `extra_args` docs explicitly call the host-artifact behavior under `--target` counterintuitive and say the same rules also apply to rustdoc flags.

## What changed in the archive

Added:

- `meta/host-target-scope-implementation-2026-03-08.md`
- `meta/frontier-salience-2026-03-08-21.md`
- `fixtures/host-target-scope-contract-kit/scope-observation.receipt.schema.json`
- `fixtures/host-target-scope-contract-kit/scope-diff.report.schema.json`
- `fixtures/host-target-scope-contract-kit/scenarios/flags_leak_to_build_script_without_explicit_target/*`
- `fixtures/host-target-scope-contract-kit/scenarios/explicit_target_same_triple_changes_scope/*`
- `fixtures/host-target-scope-contract-kit/scenarios/rustdoc_buildscript_scope_split/*`
- `fixtures/host-target-scope-contract-kit/scenarios/nightly_host_config_split/*`
- `entries/2026-03-08-144.md`

Updated:

- `proposals/cargo-host-target-scope-contract-kit.md`
- `fixtures/host-target-scope-contract-kit/README.md`
- `README.md`
- `INDEX.md`
- `meta/roadmap.md`
- `meta/research-ledger.md`
- `meta/territory-map.md`
- `meta/llm-hygiene.md`

## What should happen next

The best next passes should prefer:

1. freezing the observation and diff schemas,
2. proving adapter-free capture on a tiny real workspace,
3. and keeping host/target scope separate from linker-lane, tool-only compile, and broader target-support posture.

They should **not** drift into:

- another generic cross-build helper,
- another linker wrapper,
- or a mega Cargo doctor that absorbs rebuilds, scope, linker, and lock contention into one blurry tool.

## Sources

- Cargo configuration: https://doc.rust-lang.org/cargo/reference/config.html
- Cargo unstable features: https://doc.rust-lang.org/cargo/reference/unstable.html
- Cargo changelog: https://doc.rust-lang.org/cargo/CHANGELOG.html
- Cargo tracking issue for `target-applies-to-host`: https://github.com/rust-lang/cargo/issues/9453
- Cargo tracking issue for `host-config`: https://github.com/rust-lang/cargo/issues/9452
- Cargo issue on `RUSTFLAGS` / `--target`: https://github.com/rust-lang/cargo/issues/14046
- docs.rs issue on rustdoc/build-script cfg scope: https://github.com/rust-lang/docs.rs/issues/1580
- Cargo internal `extra_args` docs: https://doc.rust-lang.org/beta/nightly-rustc/cargo/core/compiler/build_context/target_info/fn.extra_args.html
