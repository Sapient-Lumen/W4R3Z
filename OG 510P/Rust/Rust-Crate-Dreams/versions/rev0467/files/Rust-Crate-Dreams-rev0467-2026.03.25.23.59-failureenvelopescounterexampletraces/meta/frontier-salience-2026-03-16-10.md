# Frontier salience scan — 2026-03-16 (workspace tool manifests and install policy cooldowns)

This pass did not add a new top-level proposal.
Instead, it upgraded two early archive ideas into a much sharper 2026 lane around **workspace-managed crate tools** and **install-stage policy receipts**.

The two focal crates are:

- **P-0055 Cargo Workspace Toolchain Manifest Kit**
- **P-0056 Cargo Install Policy & Cooldown Kit**

## Main judgment

The official Rust/Cargo/crates.io substrate now makes this lane more concrete than it looked when these proposals were first written.

The important signals are:

- `cargo install` still ignores packaged lockfiles by default unless `--locked` is used,
- `cargo install` now has very explicit install-root precedence, tracking metadata, and `--no-track` tradeoffs,
- Cargo external subcommands are still PATH / `$CARGO_HOME/bin` based,
- the Cargo team explicitly keeps celebrating plugin crates because Cargo cannot be everything to everyone,
- and crates.io now publishes `pubtime`, explicitly enabling future cooldown-period workflows.

Together, that suggests two distinct missing crate layers:

1. a **workspace tool manifest / lock / runner receipt** crate, and
2. an **install policy / cooldown / waiver / receipt** crate.

## Broad ranking after this pass

1. **P-0468 Cargo Resolver Explanation Kit**
2. **P-0055 Cargo Workspace Toolchain Manifest Kit**
3. **P-0056 Cargo Install Policy & Cooldown Kit**
4. **P-0489 Cargo Build-Dir Consumer Transition Kit**
5. **P-0508 Cargo Build Script Delegation Kit**
6. **P-0244 SemVer API Diff Evidence Kit**
7. **P-0507 Cargo Fix Campaign Kit**
8. **P-0478 Cargo Future-Incompat Triage Kit**
9. **P-0432 Cargo Plumbing Interop Kit**
10. **P-0484 Toolchain & Target Support Contract Kit**
11. **P-0477 Cargo Publish Receipt Join Kit**
12. **P-0480 Cargo Global Cache Policy & GC Receipt Kit**

## Why P-0055 rose now

Earlier versions of the archive knew that teams wanted workspace-scoped tool dependencies, but the proposal was still too hand-wavy.

The sharper official seam now is:

- `cargo install` is still user/system-level,
- local project config is not the default input for install flows,
- custom subcommands are still discovered through executable placement,
- and `$CARGO_HOME/bin` is shared enough that runner provenance matters.

That makes the missing crate much more specific:

- manifest + lock,
- install-root receipts,
- runner receipts,
- and rustup-context capture without pretending to be rustup.

## Why P-0056 rose now

The install-policy proposal looked interesting before, but `pubtime` changes its weight.

It is now much more plausible to build a boring crate for:

- lockfile stance,
- cooldown gates,
- tracking/no-track policy,
- and install receipts.

That is stronger than a generic “security wrapper” story.

## What this pass did not do

It did **not** collapse:

- workspace tool manifests,
- install policy and cooldowns,
- rustup compiler/toolchain contracts,
- Cargo home cache GC,
- and publish-surface identity

into one fake “tool setup crate”.

That restraint improved the archive.

## Sources

- `cargo install` docs: https://doc.rust-lang.org/cargo/commands/cargo-install.html
- `cargo` command docs: https://doc.rust-lang.org/cargo/commands/cargo.html
- Cargo external tools docs: https://doc.rust-lang.org/cargo/reference/external-tools.html
- Cargo 1.94 development-cycle update: https://blog.rust-lang.org/inside-rust/2026/02/18/this-development-cycle-in-cargo-1.94/
- crates.io development update (2026-01-21): https://blog.rust-lang.org/2026/01/21/crates-io-development-update/
- rustup overrides: https://rust-lang.github.io/rustup/overrides.html
