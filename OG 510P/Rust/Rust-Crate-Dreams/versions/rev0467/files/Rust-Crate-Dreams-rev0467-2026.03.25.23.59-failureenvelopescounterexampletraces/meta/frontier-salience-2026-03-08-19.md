# Frontier salience scan — 2026-03-08 (nineteenth pass)

## Main judgment

This pass **did** add a new top-level proposal:

- **P-0505 Cargo Host/Target Scope Contract Kit**

The repo already had strong ideas for toolchain support, linker-lane diagnosis, and tool-only Cargo workflows.
What it still lacked was a clean crate for the **scope layer** itself: one contract for intended host/target config scope, one receipt for what was actually observed, and one diagnosis/diff artifact for mixed-build drift.

That is a real missing seam rather than just another cross-compilation helper.

## Ranked frontier after this pass

1. **P-0469 Cargo Rebuild Explanation Kit**
2. **P-0468 Cargo Resolver Explanation Kit**
3. **P-0503 Assurance Case Workbench Kit**
4. **P-0504 Linker Lane Contract & Diagnosis Kit**
5. **P-0494 Cargo Compile-Time-Deps Workflow Kit**
6. **P-0505 Cargo Host/Target Scope Contract Kit**
7. **P-0486 Debuggability Support Contract Kit**
8. **P-0433 MC/DC Coverage Workbench Kit**
9. **P-0453 Safety Contract Consumer Kit**
10. **P-0490 Cargo Lock Contention Witness Kit**

## Why P-0505 is salient

Five current facts make this more than a speculative niche:

- Cargo’s config docs explicitly document that `build.rustflags` / `RUSTFLAGS` hit all compiler invocations when `--target` is absent, including build scripts and proc macros.
- Cargo’s unstable docs now expose `target-applies-to-host` and `[host]`, making host/target scope a real first-class configuration frontier.
- Cargo’s own internal docs say the host-artifact rule is counterintuitive and that the same rule family also applies to rustdoc.
- The user-wide cache and sandboxed build-script goals both treat host/target artifact sharing or separation as a meaningful substrate concern.
- Official Cargo/docs.rs issues show practical user pain around `RUSTFLAGS` scope changes and rustdoc/build-script cfg mismatches.

## What should happen next

The best next passes on this frontier should prefer:

1. tiny schema work for `scope-snapshot.manifest` and `scope-diagnosis.report`,
2. scenario bundles for `flags_leak_to_host`, `explicit_target_flips_scope`, `host_config_split`, and `rustdoc_buildscript_scope_split`,
3. comparison planning between stable legacy behavior and nightly `host-config`-based behavior,
4. and explicit boundary notes keeping scope contracts distinct from linker-lane doctors and compile-time-deps parity bundles.

They should **not** drift into:

- another linker wrapper,
- another build-script sandbox runner,
- or a giant all-purpose Cargo “doctor” that collapses every frontier together.

## Sources

- Cargo configuration: https://doc.rust-lang.org/cargo/reference/config.html
- Cargo unstable features: https://doc.rust-lang.org/cargo/reference/unstable.html
- Cargo changelog: https://doc.rust-lang.org/cargo/CHANGELOG.html
- Cargo internal target-info docs: https://doc.rust-lang.org/beta/nightly-rustc/cargo/core/compiler/build_context/target_info/fn.extra_args.html
- User-wide build cache goal: https://rust-lang.github.io/rust-project-goals/2024h2/user-wide-cache.html
- Sandboxed build scripts goal: https://rust-lang.github.io/rust-project-goals/2024h2/sandboxed-build-script.html
- Cargo issue `RUSTFLAGS` / `--target`: https://github.com/rust-lang/cargo/issues/14046
- docs.rs issue on rustdoc/build-script cfg scope: https://github.com/rust-lang/docs.rs/issues/1580
