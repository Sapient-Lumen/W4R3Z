# Gap: Airgapped bootstrapping and offline profiles in Rust

## What is missing
Rust has real primitives for offline and mirrored usage, but it still lacks a **boring, reviewable bootstrapping boundary** for restricted-network environments.

Today a team can:
- prefetch dependencies with `cargo fetch`,
- build with `--offline` or `--frozen`,
- vendor crates with `cargo vendor`,
- redirect registries with source replacement,
- run alternate registries over `git` or `sparse`,
- point `rustup` at local mirrors with `RUSTUP_DIST_SERVER` and `RUSTUP_UPDATE_ROOT`,
- and use mirror tools like ROMT or Panamax to mirror crates.io and rustup.

What is still missing is the shared layer that answers:
- which hosts, registries, and mirror roots are actually allowed,
- how dependency resolution, `cargo install`, and rustup/toolchain provisioning are supposed to work together,
- whether a workspace is really offline-safe or only “offline on one machine if caches happen to be warm”,
- how to record denied network attempts and configuration drift,
- and what CI/release artifact downstream policy and audit tooling should consume.

## Why it matters
This is not just a niche “airgapped defense contractor” problem.

Rust’s own crates.io mirroring goal explicitly says users need secure local mirrors for CI, restrictive firewalls, and unreliable internet, and it notes that roughly half of Rust release and crate traffic comes from CI providers. Cargo now has sparse registry support for crates.io on stable, and the docs explicitly support mirroring, source replacement, local registries, vendoring, and offline commands. The substrate is real.

But the end-to-end story is still fragmented:
- workspace dependencies can be prefetched or vendored,
- mirror operators can serve crates and rustup artifacts,
- yet `cargo install` has system/user-level configuration behavior that differs from ordinary workspace config discovery,
- and the “primary” documented local-registry helper is itself something you install with `cargo install`.

That means organizations still end up writing bespoke bootstrap playbooks, wrapper scripts, and compliance checklists.

## Existing building blocks worth composing
- Cargo documents `cargo fetch` as the command that makes dependencies locally available so later Cargo commands can run offline as long as the lockfile does not change.
  https://doc.rust-lang.org/cargo/commands/cargo-fetch.html
- Cargo’s FAQ says `--offline` and `--frozen` prevent network access and points users to fetch + vendoring/source replacement for offline workflows.
  https://doc.rust-lang.org/cargo/faq.html
- Cargo’s source replacement docs explicitly support mirroring, local registries, and vendored directory sources, and state that replacement sources must be exact copies of the original source.
  https://doc.rust-lang.org/cargo/reference/source-replacement.html
- Those same docs say local registry sources are typically managed by `cargo-local-registry`, installed via `cargo install cargo-local-registry`.
  https://doc.rust-lang.org/cargo/reference/source-replacement.html
- Cargo’s registries docs say alternate registries can use either `git` or `sparse`, and that sparse fetches only the metadata files needed for relevant crates.
  https://doc.rust-lang.org/cargo/reference/registries.html
- Rust release notes record that sparse registry support for crates.io was stabilized.
  https://doc.rust-lang.org/beta/releases.html
- `cargo install` explicitly says it is a system/user-level operation, ignores local project configuration discovery, and begins config discovery at `$CARGO_HOME/config.toml` unless using `--path`.
  https://doc.rust-lang.org/cargo/commands/cargo-install.html
- The rustup book documents `RUSTUP_DIST_SERVER` and `RUSTUP_UPDATE_ROOT` for using local mirrors.
  https://rust-lang.github.io/rustup/environment-variables.html
- Rust’s 2025H1 crates.io mirroring goal explicitly targets secure mirroring for restrictive firewalls, unreliable internet, and CI infrastructure.
  https://rust-lang.github.io/rust-project-goals/2025h1/verification-and-mirroring.html
- ROMT and Panamax already exist to mirror rustup and crates.io for offline usage, which is strong evidence that the operational need is real.
  https://github.com/drmikehenry/romt
  https://github.com/panamax-rs/panamax

## Why existing tools are not yet the whole answer
The ecosystem has **mirror tools and configuration primitives**, but not one **stable contract/evidence layer**.

Today teams still have to invent their own answers for:
- canonical mirror profile format,
- allowed-host policy,
- `cargo install` bootstrap behavior,
- rustup mirror binding and required component lists,
- network-attempt recording,
- and CI-friendly proof that a workspace/tool bootstrap actually passed without unexpected egress.

The result is familiar from elsewhere in the archive: strong point tools, weak shared artifacts.

## Target outcome
A project or organization should be able to say:
- “these are the only permitted crate/toolchain sources,”
- “this is how rustup, workspace builds, and developer-tool installs are expected to resolve,”
- “this workspace/toolchain passed restricted-network validation under these exact conditions,”
- “these network attempts were denied or never occurred,”
- and “this is the portable pack CI, auditors, and downstream teams can consume.”

That is bigger than a mirror daemon and smaller than trying to standardize every registry or enterprise artifact server in one move.
