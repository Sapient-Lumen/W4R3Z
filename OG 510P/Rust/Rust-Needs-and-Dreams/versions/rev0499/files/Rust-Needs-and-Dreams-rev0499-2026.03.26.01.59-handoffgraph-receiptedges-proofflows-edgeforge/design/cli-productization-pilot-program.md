# Design: CLI Productization Pilot Program

## Goal
Turn the archive’s **real-tool seam** into an executable program instead of scattered good ideas.

The pilot program couples:
- [`design/command-surface-kit.md`](./command-surface-kit.md)
- [`design/terminal-surface-kit.md`](./terminal-surface-kit.md)
- [`design/runtime-settings-kit.md`](./runtime-settings-kit.md)
- [`design/cli-productization-stack.md`](./cli-productization-stack.md)
- [`design/distribution-contract-stack.md`](./distribution-contract-stack.md)
- [`design/support-envelope-kit.md`](./support-envelope-kit.md)
- [`design/docproof-kit.md`](./docproof-kit.md)

The central thesis is that Rust now has enough parser, terminal, and distribution ingredients that the next missing thing is **tool productization evidence**, not another framework bake-off.

## Why this now deserves a pilot program
- Rust is explicitly trying to make high-level utility use cases easier with the `cargo script` goal, framing single-file Rust utilities, examples, and reproducible bug reports as important user flows.
  - https://rust-lang.github.io/rust-project-goals/
- Cargo custom subcommands are already a native ecosystem lane with forwarded args and `cargo help` integration, which means a large class of Rust tools live inside the Cargo UX rather than outside it.
  - https://doc.rust-lang.org/cargo/reference/external-tools.html
- `clap` already points to shell completion, manpage generation, testing, and the Rust CLI book around the core parser model, which is exactly the pattern that usually precedes a missing productization layer.
  - https://docs.rs/clap/latest/clap/
  - https://docs.rs/clap_complete/latest/clap_complete/env/
  - https://docs.rs/clap_mangen/latest/clap_mangen/
- The Rust CLI book explicitly treats output policy, testing, and packaging/distribution as part of serious CLI design rather than optional polish.
  - https://rust-cli.github.io/book/tutorial/output.html
  - https://rust-cli.github.io/book/tutorial/testing.html
  - https://rust-cli.github.io/book/tutorial/packaging.html
- `cargo-dist` and `cargo-binstall` prove that real users already care about prebuilt acquisition, manifests, installers, and fallback paths rather than only `cargo install`.
  - https://github.com/axodotdev/cargo-dist
  - https://github.com/cargo-bins/cargo-binstall
- Terminal behavior is visibly its own support surface: `crossterm` exposes cross-platform terminal actions and flush semantics, Ratatui owns buffered frame rendering and restore/setup helpers, and `anstream` owns stream-sensitive color behavior with env and Windows-console handling.
  - https://docs.rs/crossterm/latest/crossterm/
  - https://docs.rs/ratatui/latest/ratatui/struct.Terminal.html
  - https://docs.rs/anstream/latest/anstream/struct.AutoStream.html

## Strategic posture
This should be treated as a **companion evidence substrate**, not as a bid to replace today’s tool crates.

- Command Surface owns parse/help/completion/manpage truth.
- Terminal Surface owns live terminal semantics.
- Runtime Settings owns config/env/cache/state activation.
- Consumer Install owns acquisition/install truth, while Update Continuity owns post-install mutation truth.
- Support Envelope + DocProof own support/docs truth.
- release/support/atlas consumers import these artifacts instead of re-deriving them from repo folklore.

## Ranked pilot order

### Pilot 1 — Classic CLI lane
**Shape**
- clap-based standalone CLI with help, examples, completions, and manpage generation.

**Why first**
- smallest surface area with strong real-world relevance;
- already exercises the most obvious generated/documented tool surfaces.

**Must prove**
- `command-pack/v0` can attach help/completion/manpage/example evidence honestly;
- illustrative examples stay distinct from checked transcripts;
- install snippets and support notes can import command truth without redefining it.

### Pilot 2 — Cargo subcommand lane
**Shape**
- `cargo-*` tool with standalone binary identity and Cargo-invocation identity.

**Why second**
- proves the ecosystem-native extension lane is first-class;
- forces explicit identity/help/install semantics.

**Must prove**
- cargo-subcommand identity stays separate from package/binary identity;
- `cargo help` posture and forwarded-argument semantics are documented rather than assumed;
- source-build versus prebuilt install posture is reviewable.

### Pilot 3 — Machine-output operator lane
**Shape**
- CLI with JSON/plain/progress/quiet/verbose modes and scripting expectations.

**Why third**
- reveals the human-vs-machine contract problem clearly;
- matters to CI and automation consumers immediately.

**Must prove**
- stdout/stderr/progress posture is explicit;
- machine-readable output is versioned separately from human-friendly text;
- runtime/config state and transcript expectations are attachable evidence.

### Pilot 4 — Terminal/TUI lane
**Shape**
- terminal app or TUI importing `terminal-pack/v0` with raw mode / alternate screen / resize / color / layout truth.

**Why fourth**
- exercises the richer runtime-semantics lane without pretending every tool needs it.

**Must prove**
- command truth and terminal truth stay distinct;
- cleanup/restore guarantees and fallback behavior become visible;
- support/docs can cite terminal assumptions honestly.

### Pilot 5 — Install/update/support lane
**Shape**
- one tool distributed through multiple acquisition paths (for example source-build, direct release, package manager, or `cargo binstall`).

**Why fifth**
- proves the stack matters after build time and before incident archaeology.

**Must prove**
- install receipts and fallback reasons are reviewable;
- support matrices can distinguish officially supported install paths from tolerated ones;
- docs/install snippets stay checked against actual acquisition posture.

## Shared artifact family
### Lower-layer artifacts
- `command-pack/v0`
- `terminal-pack/v0`
- runtime-settings reports / packs
- distribution/install receipts
- support/docs reports

### Aggregate layer
- `cli-product-pack/v0`
  - a thin referenced pack importing the lower-layer artifacts
  - never a new truth engine that rewrites those layers

## Cross-kit boundaries
- **Command Surface Kit** keeps owning parse/help/completion/manpage semantics.
- **Terminal Surface Kit** keeps owning terminal/input/render/layout semantics.
- **Runtime Settings Kit** keeps owning config/default/source/secret/cache activation.
- **Consumer Install Kit** keeps owning acquisition/install truth, while **Update Continuity Kit** keeps owning post-install mutation truth.
- **Support Envelope + DocProof** keep owning support matrices and checked docs/examples.
- **Release Truth Stack** stays a producer-side import, not the consumer-side install truth itself.

## Pilot scorecard
A pilot only graduates if it shows all of the following:
1. **User-facing legibility** — a reviewer can tell what the tool claims without reverse-engineering its repo.
2. **Layer honesty** — command, terminal, runtime, install, and support truths remain distinct.
3. **Diffability** — drift in help, terminal posture, config activation, or install support is reason-coded.
4. **Consumer usefulness** — release/support/docs/atlas consumers can import the results directly.
5. **No framework capture** — the artifacts remain useful across more than one parser/terminal/distribution stack.

## Anti-goals
- not a replacement for `clap`, Ratatui, `crossterm`, or the Rust CLI book;
- not another CLI generator or TUI framework;
- not a new installer monopoly or self-update regime;
- not a fake “tool readiness” score.
