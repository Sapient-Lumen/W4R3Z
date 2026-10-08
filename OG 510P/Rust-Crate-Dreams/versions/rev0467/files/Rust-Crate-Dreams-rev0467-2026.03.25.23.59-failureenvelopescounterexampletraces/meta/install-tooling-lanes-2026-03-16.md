# Install tooling lanes — 2026-03-16

This note exists to keep future archive passes from collapsing several adjacent but distinct Rust tooling problems into one vague “tool install” crate.

## Main judgment

The Rust ecosystem now has enough official install and registry substrate that the sharper missing crates are **coordination artifacts above the substrate**, not one giant manager.

The lanes that must stay separate are:

1. **workspace-scoped tool dependency manifests and runner receipts**
   - example: **P-0055 Cargo Workspace Toolchain Manifest Kit**
   - owns: repo-local tool intent, lockfiles, install-root selection, runner shims, run receipts
2. **install policy, cooldowns, and install-stage receipts**
   - example: **P-0056 Cargo Install Policy & Cooldown Kit**
   - owns: lockfile stance, `pubtime` age gates, allowed sources, tracking mode, waivers, install receipts
3. **rustup compiler/toolchain support contracts**
   - example: **P-0484 Toolchain & Target Support Contract Kit**
   - owns: compiler channel/profile/components/targets/support posture, not crate-shipped auxiliary tools
4. **global cache retention and garbage-collection policy**
   - example: **P-0480 Cargo Global Cache Policy & GC Receipt Kit**
   - owns: Cargo home caches and cleanup policy, not install selection or runner intent
5. **publish-surface identity and release receipts**
   - examples: **P-0175** and **P-0477**
   - owns: publish auth/rehearsal and post-publish facts, not install-time tool management

## Working rule

If a future pass touches tool installation, ask first whether the missing value is:

- a **workspace tool manifest / lock / runner**,
- an **install policy / cooldown / waiver** layer,
- a **rustup compiler support contract**,
- a **Cargo home cache policy**,
- or a **publish/release artifact**.

Do **not** let the archive silently flatten those into one fake “tooling setup crate”.

## Why this matters now

Fresh official Cargo and crates.io facts make the distinctions more important:

- `cargo install` is still a user/system-level install command with specific install-root and lockfile behavior,
- Cargo custom subcommands still depend on PATH / `$CARGO_HOME/bin` discovery,
- crates.io now publishes `pubtime`, enabling age-gate policy workflows,
- and rustup still owns compiler/toolchain override behavior.

That means the strongest missing crates here are layered and narrow:

- one crate for **workspace tool intent**,
- one crate for **install-stage policy**,
- and adjacent crates for **toolchain support**, **cache hygiene**, and **publish facts**.

## Sources

- `cargo install` docs: https://doc.rust-lang.org/cargo/commands/cargo-install.html
- `cargo` command docs: https://doc.rust-lang.org/cargo/commands/cargo.html
- Cargo external tools docs: https://doc.rust-lang.org/cargo/reference/external-tools.html
- crates.io development update (2026-01-21): https://blog.rust-lang.org/2026/01/21/crates-io-development-update/
- rustup overrides: https://rust-lang.github.io/rustup/overrides.html
