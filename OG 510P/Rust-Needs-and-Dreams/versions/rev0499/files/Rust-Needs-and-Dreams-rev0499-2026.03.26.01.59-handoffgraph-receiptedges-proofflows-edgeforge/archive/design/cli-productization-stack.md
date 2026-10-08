# Design note: CLI Productization Stack (Command Surface + Terminal Surface + Runtime Settings + Distribution Contract + Update Continuity + Support Envelope)

## Goal
Define the **division of labor and consumer flow** between Rust command surfaces, terminal semantics, runtime settings, install/update truth, and support/docs claims so the ecosystem can make **real CLI tools, cargo subcommands, terminal apps, and operator-facing utilities** reviewable without anointing one parser crate, one terminal stack, one installer, or one TUI framework as the answer.

This is **not** a new top-level mega-framework.
It is a stack note explaining how existing archive pieces should compose:
- [`design/command-surface-kit.md`](./command-surface-kit.md)
- [`design/terminal-surface-kit.md`](./terminal-surface-kit.md)
- [`design/runtime-settings-kit.md`](./runtime-settings-kit.md)
- [`design/distribution-contract-stack.md`](./distribution-contract-stack.md)
- [`design/update-continuity-kit.md`](./update-continuity-kit.md)
- [`design/support-envelope-kit.md`](./support-envelope-kit.md)
- [`design/docproof-kit.md`](./docproof-kit.md)
- [`design/release-pipeline-kit.md`](./release-pipeline-kit.md)

## Why this note is needed now
Rust’s current signals no longer say only “CLIs are possible.” They say Rust already has serious tool-making ingredients, but still lacks the **productization layer above them**:
- the 2025H2 goals explicitly say Rust wants to stabilize `cargo script` so single-file Rust programs can more easily power small utilities, shared examples, and reproducible bug reports;
- Cargo’s external-tools model makes `cargo-*` subcommands a first-class Rust extension lane, with forwarded arguments and `cargo help` integration;
- `clap` already anchors a rich command surface and explicitly points to manpage generation, shell completion, testing, and command-line app docs as part of the ecosystem around it;
- `clap_complete` explicitly warns that dynamic completion shell code can mismatch the program after upgrades, which is strong evidence that completion/install/update behavior is a product surface rather than disposable glue;
- the Rust CLI book treats output policy, testing, packaging, and distribution as core tool-design concerns rather than afterthoughts;
- `cargo-dist` and `cargo-binstall` already prove that plan/build/install/update/distribution concerns are real and separate from building the binary from source;
- `crossterm`, Ratatui, and `anstream` show that terminal and output semantics are their own layers: flush behavior, color negotiation, raw mode, alternate screen, resize/input, Windows console fallback, and other terminal realities do not disappear just because a parser worked.

Together these signals justify treating CLI productization as a **frontier-worthy ecosystem seam** instead of leaving Rust tools split across parser definitions, generated completions, terminal stacks, release jobs, and README installation prose.

## Stack layers

### 1) Command Surface: the declared tool boundary
Command Surface owns the **declared user-facing command interface**:
- subcommands, flags, arguments, and value hints
- help/version surfaces
- completion and manpage generation posture
- cargo-subcommand identity where relevant
- output-mode declarations where they belong to the command contract
- checked transcripts, snapshots, and drift reports

Command Surface answers questions like:
- “What does this tool claim to parse and expose?”
- “Which completions/manpages are generated and versioned?”
- “Is this a standalone binary, a cargo subcommand, or both?”

Design rule: **command truth must stay separate from terminal truth and install truth**.
A parser declaration is not a runtime-terminal contract and not an install receipt.

### 2) Terminal Surface: the live interaction boundary
Terminal Surface owns the **runtime terminal semantics** of the tool:
- TTY assumptions
- color/style negotiation
- raw mode / alternate screen / cleanup posture
- input-event families and resize handling
- Unicode layout/rendering policy
- full-screen or line-editor posture when relevant

Terminal Surface answers questions like:
- “Does this tool require a real terminal?”
- “Does it work as plain stdout/stderr or does it enter a managed terminal mode?”
- “What happens on non-TTYs, narrow terminals, or Windows consoles?”

Design rule: **terminal behavior must not be inferred from screenshots, backend choice, or issue comments**.

### 3) Runtime Settings: activation and configuration truth
Runtime Settings owns the **activation/configuration boundary**:
- config files and discovery order
- env vars and profile selection
- cache/data/state directories
- local-vs-global settings posture
- optional credentials or secret references when a tool actually uses them

Runtime Settings answers questions like:
- “Which configuration knobs exist and how are they activated?”
- “What defaults are real versus illustrative?”
- “Which runtime state locations matter for support and reproducibility?”

Design rule: **tool behavior must not be explained only by a README env-var section or hidden dotfiles**.

### 4) Consumer Install + Update Continuity: acquisition, install, and lifecycle truth
Consumer Install owns the **first-install acquisition boundary**, while Update Continuity owns post-install mutation:
- source-build versus prebuilt versus package-manager paths
- selection/fallback order
- verification/signature posture
- install receipts and update-continuity imports
- mirror/offline posture where relevant

Distribution Contract answers questions like:
- “How did the user or CI actually obtain this tool?”
- “Was this a `cargo install`, `cargo binstall`, package-manager, or direct-release path?”
- “What changed on disk and what verification ran?”

Design rule: **release artifacts, first-install receipts, and later update continuity are related but not identical truths**.

### 5) Update Continuity: lifecycle change after install
Update Continuity owns the **post-install mutation boundary**:
- current installed-subject identity
- candidate/comparator and hold/downgrade policy
- chosen update plan and delegated-manager posture
- apply/rollback/uninstall results
- managed-content ownership and cleanup scope

Update Continuity answers questions like:
- “What version or install state did this tool start from?”
- “What update candidate was chosen and why?”
- “What actually changed on disk, what failed, and what can be rolled back or safely uninstalled?”

Design rule: **install receipts and update continuity are related but not identical truths**.

### 6) Support Envelope + DocProof: support and docs truth
Support Envelope and DocProof together own the **supportability boundary**:
- supported shells, platforms, and runtime floors
- source-build versus released-binary posture
- checked docs/examples/install snippets
- command transcripts and support references
- best-effort versus official support posture

This layer answers questions like:
- “Which shells/platforms are truly supported?”
- “Are docs, install snippets, and examples actually checked?”
- “What does the project support versus merely tolerate?”

Design rule: **one working local install or one green CI job is not the support contract**.

### 7) Downstream consumers
The stack becomes worthy when real consumers can import it without flattening it:
- **Release/review** consumers can attach command, terminal, install, and support evidence to real releases.
- **Support/incident** consumers can reconstruct user-facing behavior from product artifacts instead of screenshots and chat logs.
- **Atlas/learning** consumers can recommend serious Rust tool stacks without pretending all CLIs or terminal apps have the same needs.
- **LLM/editor/documentation** consumers can read a portable tool story instead of scraping mixed prose and generated files.

Design rule: **consumers import selected evidence; they do not redefine the tool truth models**.

## What an epic contribution should look like in practice
A worthy contribution here is not “build the one true Rust CLI framework.”
It is a portable, reviewable stack with clear boundaries:

1. **command truth first**
   - prove `command-surface/v0` and `command-pack/v0` on one real tool;
2. **terminal truth second**
   - attach `terminal-pack/v0` where interaction is more than plain stdout/stderr;
3. **runtime-settings truth third**
   - make config/env/cache/state activation explicit and diffable;
4. **install/lifecycle/support truth fourth**
   - prove prebuilt/package-manager/source-build/install-snippet differences can be described honestly;
5. **consumer proofs fifth**
   - show release/support/docs/atlas consumers can import the artifacts without re-deriving them from repo folklore.

An eventual aggregate artifact may exist, but it should be a **thin referenced pack** such as `cli-product-pack/v0`, not a new truth engine that erases command, terminal, config, distribution, and support boundaries.

## Ranked first execution lanes
1. **Classic clap-based CLI lane**
   - best first exporter because it exercises help, completions, manpages, examples, and install guidance without needing a full-screen terminal.
2. **Cargo subcommand lane**
   - proves command identity, help forwarding, Cargo invocation posture, and install expectations stay explicit.
3. **Machine-readable operator-tool lane**
   - proves human-vs-machine output, stderr/stdout, quiet/verbose, and transcript truth can be reviewed as contracts.
4. **Terminal/TUI lane**
   - imports Terminal Surface for raw mode, alternate screen, color/layout/input semantics, and cleanup guarantees.
5. **Install/update/support lane**
   - proves direct release, package-manager, and source-build paths can all attach honest support and receipt evidence.

## Non-goals
- one universal parser or subcommand framework;
- one universal TUI or REPL framework;
- another installer wrapper that hides acquisition truth;
- flattening command semantics, terminal semantics, runtime settings, install receipts, and support claims into one fake “CLI readiness” schema;
- pretending shell completions, screenshots, or release artifacts alone prove product quality.

## Archive implications
- The archive should now treat **Command Surface + Terminal Surface + Runtime Settings + Distribution Contract + Support Envelope** as a coupled **CLI Productization Stack** in frontier discussions.
- Future revisions should prefer **parser/help/completion/manpage truth, terminal/raw-mode/color/layout truth, machine-vs-human output posture, runtime-setting activation, install receipts, update continuity, and support/docs truth** over another parser framework, TUI shell, installer wrapper, self-update helper, or shell-completion-only crate.
- When Distribution, Release, Support, Atlas, or Documentation work cites tool readiness, they should import **command truth**, **terminal truth**, **runtime-settings truth**, **install truth**, and **support truth** separately.

## References (signals)
- Rust project goals / `cargo script`:
  https://rust-lang.github.io/rust-project-goals/
- Cargo custom subcommands:
  https://doc.rust-lang.org/cargo/reference/external-tools.html
- clap ecosystem docs:
  https://docs.rs/clap/latest/clap/
  https://docs.rs/clap_complete/latest/clap_complete/env/
  https://docs.rs/clap_mangen/latest/clap_mangen/
- Rust CLI book:
  https://rust-cli.github.io/book/tutorial/output.html
  https://rust-cli.github.io/book/tutorial/testing.html
  https://rust-cli.github.io/book/tutorial/packaging.html
- cargo-dist / cargo-binstall:
  https://github.com/axodotdev/cargo-dist
  https://github.com/cargo-bins/cargo-binstall
- terminal/output layers:
  https://docs.rs/crossterm/latest/crossterm/
  https://docs.rs/ratatui/latest/ratatui/struct.Terminal.html
  https://docs.rs/anstream/latest/anstream/struct.AutoStream.html
