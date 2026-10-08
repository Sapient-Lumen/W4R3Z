# Host/target scope implementation note — 2026-03-08

## Main judgment

**P-0505 Cargo Host/Target Scope Contract Kit** is now far enough along that the next useful work is schema and scenario freezing, not more ideation.

## Why this frontier strengthened

The official Cargo docs and issue tracker now support a very specific product shape:

- stable docs already define the `RUSTFLAGS` / `build.rustflags` split around `--target`,
- unstable docs and tracking issues still show `host-config` and `target-applies-to-host` as live, baking surfaces,
- Cargo internal docs explicitly describe host-artifact behavior under `--target` as counterintuitive and note that the same rule family also applies to rustdoc flags,
- issue reports show this causing real maintainer surprise for both build scripts and docs-builder-like flows.

That means the missing crate does not need to speculate about whether the seam exists.
It should freeze that seam into one **portable incident bundle**.

## Immediate implementation targets

1. freeze `scope-observation.receipt.json`,
2. freeze `scope-diff.report.json`,
3. keep `same_triple_lane_changed` separate from ordinary `target_only_shift`,
4. and prove the vocabulary on four tiny scenarios before inventing adapters or auto-fixes.

## Anti-patterns to avoid

- another generic cross-compilation helper,
- another linker wrapper,
- treating host==target triple strings as proof that nothing changed,
- or promising perfect command reconstruction when some facts are only conservative inference.

## Sources

- Cargo configuration: https://doc.rust-lang.org/cargo/reference/config.html
- Cargo unstable features: https://doc.rust-lang.org/cargo/reference/unstable.html
- Cargo tracking issue for `target-applies-to-host`: https://github.com/rust-lang/cargo/issues/9453
- Cargo tracking issue for `host-config`: https://github.com/rust-lang/cargo/issues/9452
- Cargo issue on `RUSTFLAGS` / `--target`: https://github.com/rust-lang/cargo/issues/14046
- docs.rs issue on rustdoc/build-script cfg scope: https://github.com/rust-lang/docs.rs/issues/1580
- Cargo internal `extra_args` docs: https://doc.rust-lang.org/beta/nightly-rustc/cargo/core/compiler/build_context/target_info/fn.extra_args.html
