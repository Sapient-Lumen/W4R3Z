# Host/target scope upstream fit — 2026-03-08

## Main judgment

This frontier now has enough official substrate that the missing value is **not another blog post, config snippet collection, or linker wrapper**.

The missing value is the **scope contract / observation / diagnosis / diff layer** above Cargo’s existing config surfaces.

## Current substrate we should treat as real

- Cargo configuration docs already state how `build.rustflags` / `RUSTFLAGS` behave with and without `--target`.
- Cargo configuration docs also expose the same layered surface for `build.rustdocflags` and target-specific `rustdocflags`.
- Cargo’s unstable docs already expose `target-applies-to-host` and `[host]`, which means the project has admitted this seam is important enough to model explicitly.
- Cargo’s own internal docs say host-artifact behavior under these rules is counterintuitive, and that the same rule family also applies to rustdoc.
- The user-wide cache and sandboxed build-script goals both explicitly depend on host/target artifact sharing or separation.

## Prior art and evidence we should not ignore

- Official Cargo issue reports about `RUSTFLAGS` changing behavior when `--target` is added.
- Official docs.rs issue reports about rustdoc cfgs and build-script cfgs diverging in docs-builder-like workflows.

These are not proof the problem is solved.
They are proof that the **scope seam is real** and user-facing.

## Planning rule

When a future pass touches build scripts, proc macros, rustdoc flags, `RUSTFLAGS`, `RUSTDOCFLAGS`, `host-config`, or `target-applies-to-host`, it must state explicitly whether the missing value is:

1. broader **toolchain/target support posture**,
2. a **tool-only compile-surface parity** bundle,
3. a **linker-lane contract/doctor**,
4. or a **host/target scope contract and diagnosis** layer.

For this archive, the best current move is (4), not another broad hybrid of (1)–(3).

## Adjacent boundaries to keep sharp

- **P-0484 Toolchain & Target Support Contract Kit** is broader support posture.
- **P-0494 Cargo Compile-Time-Deps Workflow Kit** is tool-only / editor-oriented build-surface parity.
- **P-0504 Linker Lane Contract & Diagnosis Kit** is about linker lane choice, failure classes, and lane-switch risk.
- **P-0505** should stay on **host/target scope intent, observation, and mixed-build drift**.

## Sources

- Cargo configuration: https://doc.rust-lang.org/cargo/reference/config.html
- Cargo unstable features (`host-config`, `target-applies-to-host`): https://doc.rust-lang.org/cargo/reference/unstable.html
- Cargo changelog: https://doc.rust-lang.org/cargo/CHANGELOG.html
- Cargo internal target-info docs: https://doc.rust-lang.org/beta/nightly-rustc/cargo/core/compiler/build_context/target_info/fn.extra_args.html
- User-wide build cache goal: https://rust-lang.github.io/rust-project-goals/2024h2/user-wide-cache.html
- Sandboxed build scripts goal: https://rust-lang.github.io/rust-project-goals/2024h2/sandboxed-build-script.html
- Cargo issue on `RUSTFLAGS` / `--target`: https://github.com/rust-lang/cargo/issues/14046
- docs.rs issue on rustdoc/build-script cfg scope: https://github.com/rust-lang/docs.rs/issues/1580
