# Frontier salience snapshot — 2026-03-21-138

This pass did **not** add another binary installer, shell bootstrapper, or cargo-plugin launcher.
It sharpened **P-0055 Cargo Workspace Toolchain Manifest Kit** into a more route-aware workspace tool-dependency contract.

## Why this frontier moved up

Cargo’s tool-discovery and install substrate is now precise enough that the sharper missing layer is increasingly obvious:

- `cargo install` explicitly operates at the **system/user** level rather than the project level and ignores local config discovery except in `--path` cases;
- Cargo’s install docs make installation-root choice explicit and note that installed executables land in the chosen root’s `bin` directory;
- Cargo’s external-tools docs say custom subcommands are resolved from `cargo-${command}` executables on PATH and that Cargo defaults to preferring **`$CARGO_HOME/bin`** over the rest of PATH;
- rustup override docs make per-directory overrides, `rust-toolchain.toml`, and `cargo +toolchain ...` first-class sources of execution-context drift;
- the long-running Cargo issue about making command binaries available from dev-dependencies is still open and still labeled `needs-design`;
- and third-party crates like `cargo-run-bin` and `cargo-binstall` prove there is real demand for project-local execution and alternate installation strategies, but they do not provide one receiver-facing workspace contract for install roots, route authority, and toolchain context.

That combination means the missing crate is not another downloader.
The missing crate is now a **workspace tool dependency contract** that can publish **install-root posture**, **tool-route authority**, and **shadowing/context honesty** above today’s Cargo and rustup substrate.

## Main conclusion

Promote **P-0055** upward again, but keep it narrow.
The next worthy move is not a package-manager competitor and not a hidden PATH manager.

It should stay focused on:

1. freezing workspace tool declarations into a reviewable manifest + lock,
2. making **where tools are installed** explicit,
3. making **which executable actually won resolution** explicit,
4. preserving **rustup/toolchain context** as imported run truth,
5. and downgrading “repo-pinned tool” claims when the route actually came from `$CARGO_HOME/bin`, another PATH entry, or a manual binary.

## Ranked near-term frontier from this pass

1. **P-0055 Cargo Workspace Toolchain Manifest Kit** — strengthened because the Cargo/rustup substrate is clear enough to build against while project-scoped tool dependencies remain a real unmet need.
2. **P-0492 Cargo Registry Auth Doctor Kit** — still strong because provider chains and operation-stage diagnosis remain broad pain for teams with alternative registries.
3. **P-0036 MSRV Workspace Lab** — still strong because workspace policy drift and command-family floors remain common support pain.
4. **P-0489 Cargo Build-Dir Consumer Transition Kit** — still strong because build-layout changes keep pressuring downstream tooling to publish honest receipts.
5. **P-0472 docs.rs Build Parity Evidence Kit** — still strong because hosted-build drift remains adjacent to toolchain and workspace support claims.

## Keep these boundaries sharp

- **P-0055** is the workspace tool dependency / install-root / route-authority contract.
- **P-0492** is registry-auth diagnosis.
- **P-0036** is MSRV and command-floor policy.
- **P-0489** is build-dir migration.
- **P-0472** is hosted documentation build parity.

Do not let “developer tooling support” flatten those lanes into one fake crate.
