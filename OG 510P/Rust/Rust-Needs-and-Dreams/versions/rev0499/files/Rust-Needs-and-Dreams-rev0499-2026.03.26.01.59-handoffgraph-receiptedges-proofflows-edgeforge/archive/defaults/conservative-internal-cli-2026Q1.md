# Default card: Conservative internal CLI / automation (2026 Q1)

Latest renewal receipt: `evidence/conservative-internal-cli-2026Q1-renewal-2026-03-22.md`


## Scope
This card applies to:
- internal CLI tools,
- operator-facing automation,
- developer utilities,
- repository or CI helper binaries,
- and non-`no_std` command-line tools where **boring maintainability** matters more than maximal minimalism.

Assumptions:
- stable Rust;
- ordinary Cargo workflows;
- workstation + CI environments;
- team ranges from Rust-new to mixed-experience;
- support posture is conservative/internal rather than mass-consumer UX polish.

This is **not** the default for:
- `no_std` or embedded CLIs;
- code-size-above-all utilities;
- public end-user desktop-grade CLIs with heavy UX/runtime expectations;
- or script/repro lanes that should stay in `cargo script` / single-file territory longer.

## Why this default now
Rust’s ecosystem-navigation problem shows up especially clearly in CLI work because the ecosystem is already strong there: the challenge is rarely “is there anything available?” and more often “which of several respectable lanes should we normalize on?”.

The archive’s current answer for this exact scope is:
**a typed, clap-first, serde-shaped, tracing-capable CLI lane with anyhow-at-the-binary-boundary and thiserror for structured internal error types.**

Why this wins here:
- Clap has unusually strong canonical docs: tutorial, reference, cookbook, CLI concepts, and FAQ all live together.
  https://docs.rs/clap/latest/clap/
  https://docs.rs/clap/latest/clap/_derive/_tutorial/index.html
- Serde remains the ecosystem’s generic data-model layer, which keeps config and data interchange boring.
  https://serde.rs/
  https://serde.rs/derive.html
- `tracing-subscriber` provides the standard structured-diagnostics entry lane, including `fmt` output and `EnvFilter`/`RUST_LOG` control.
  https://docs.rs/tracing-subscriber/latest/tracing_subscriber/fmt/
  https://docs.rs/tracing-subscriber/latest/tracing_subscriber/fmt/fn.init.html
  https://docs.rs/tracing-subscriber/latest/tracing_subscriber/filter/struct.EnvFilter.html
- `anyhow` is explicitly positioned for idiomatic application error handling, while `thiserror` gives a light derive path for structured internal error enums.
  https://docs.rs/anyhow/latest/anyhow/
  https://docs.rs/thiserror/latest/thiserror/

The point is not that these crates are eternal winners.
The point is that, for this scope, they currently form the clearest reusable **conservative internal-tool lane**.

## Default lane summary
### Default lane
- argument parsing: **clap derive**
- typed config/data model: **serde derives**
- diagnostics/logging: **tracing + tracing-subscriber**
- binary-boundary error handling: **anyhow**
- structured internal error enums where useful: **thiserror**

### Serious alternative
- parser: **argh** when code size or Fuchsia-style commandline conformance is unusually important.
  https://docs.rs/argh/latest/argh/
  https://docs.rs/argh/latest/argh/derive.FromArgs.html

### Watch / not-default here
- richer report handlers like `color-eyre` can be excellent for operator-facing diagnostics, but they are an *optional* embellishment, not part of the conservative baseline.
  https://docs.rs/color-eyre/latest/color_eyre/

## Slot guidance
### Parser slot
Prefer `clap` for the default because its canon and feature surface make it the safest reusable baseline for mixed-experience teams.
Use `argh` when code size and minimal surface are more important than clap’s broader ergonomics and ecosystem expectations.

### Config / data slot
Prefer typed config/data structures with Serde derives.
Do not start with a highly magical config stack unless the project class clearly needs layered sources, environment projection, or dynamic merging.

### Error slot
At the binary edge, prefer `anyhow::Result` and explicit context.
Inside reusable modules, prefer named error enums with `thiserror` when the distinction between error kinds matters operationally or for tests.

### Diagnostics slot
Default to `tracing-subscriber` with `fmt` and `EnvFilter` support.
For tiny tools, stdout/stderr-only is fine, but the reusable default should leave room for structured diagnostics because many “internal tools” quietly turn into important operational paths.

## Serious alternatives and when they win
### `argh` wins when
- code size matters a lot;
- the command surface is intentionally small;
- or the team values a more minimal parser surface over clap’s broader feature/documentation envelope.

### `color-eyre` or `eyre` win when
- operator-facing rich reports are a real part of the tool’s value;
- panic/report formatting is part of the user experience;
- or the tool is more support-heavy than automation-heavy.

## Escalate to a project-specific brief when
- the CLI is public-facing enough that UX polish, completions, manpages, shell integration, and support commitments dominate;
- code size/startup size or `no_std` constraints are strong;
- the command surface is plugin-hosted or extension-oriented;
- the CLI is only a thin front-end to a larger async/service/control-plane system;
- or local institutional overlays already require a different logging, policy, or bootstrap posture.

## Canonical references
- Clap overview and derive tutorial:
  https://docs.rs/clap/latest/clap/
  https://docs.rs/clap/latest/clap/_derive/_tutorial/index.html
- `argh` overview:
  https://docs.rs/argh/latest/argh/
- Serde overview and derives:
  https://serde.rs/
  https://serde.rs/derive.html
- `tracing-subscriber` formatting and filtering:
  https://docs.rs/tracing-subscriber/latest/tracing_subscriber/fmt/
  https://docs.rs/tracing-subscriber/latest/tracing_subscriber/filter/struct.EnvFilter.html
- `anyhow`:
  https://docs.rs/anyhow/latest/anyhow/
- `thiserror`:
  https://docs.rs/thiserror/latest/thiserror/

## Renewal inputs
Recheck before renewal:
- canonical parser/docs surfaces for clap and argh;
- crates.io Security tab / source-link / Trusted Publishing posture where relevant;
- obvious ecosystem shifts around single-file scripts and tiny-tool ergonomics;
- whether the default should split more sharply between internal automation and consumer-facing CLI lanes.

Signal refs:
- https://blog.rust-lang.org/2026/01/21/crates-io-development-update/
- https://rust-lang.github.io/rust-project-goals/2026/flagships.html

## Non-goals
- declaring clap the universal answer for all Rust CLIs;
- choosing a full config framework here;
- flattening internal and consumer-grade CLIs into one lane;
- pretending this card replaces command-surface, bootstrap, or package-admission review.
