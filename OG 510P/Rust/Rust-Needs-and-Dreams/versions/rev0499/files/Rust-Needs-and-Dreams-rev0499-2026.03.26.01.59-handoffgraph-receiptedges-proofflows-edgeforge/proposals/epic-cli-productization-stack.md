# Epic proposal: CLI Productization Stack

## Thesis
One of the more worthy ecosystem contributions in Rust now would be a **portable productization layer for CLI tools, cargo subcommands, terminal apps, and operator-facing utilities**.

Rust is already strong at building tools.
The missing thing is not another parser or terminal framework nearly as much as it is a boring way to publish:
- what the tool declares,
- how it behaves when attached to a real terminal,
- how it is configured,
- how users actually acquire and update it,
- and what support/docs claims are really backed by evidence.

Rust does not need one more tool-making framework nearly as much as it needs a **reviewable `cli-product-pack/v0`**.

## Why now
The timing is unusually good:
- the 2025H2 goals explicitly say Rust wants `cargo script` to make small utilities, examples, and reproducible bug reports easier;
- Cargo custom subcommands are already a native ecosystem extension lane;
- `clap` already sits at the center of a larger ecosystem including completions, manpages, testing, and command-line app documentation;
- `clap_complete` explicitly documents upgrade mismatch risk for dynamic completions, which is exactly the kind of product surface the archive should treat seriously;
- the Rust CLI book already normalizes output policy, testing, and packaging as serious CLI concerns;
- `cargo-dist` and `cargo-binstall` already prove acquisition/distribution/update flows are real Rust-tool concerns;
- and terminal behavior is already substantive enough that `crossterm`, Ratatui, and `anstream` each own materially different parts of the story.

That means the next serious seam is visible before it has converged.
This is exactly when a reviewable contract is more valuable than another framework abstraction.

Sources:
- https://rust-lang.github.io/rust-project-goals/
- https://doc.rust-lang.org/cargo/reference/external-tools.html
- https://docs.rs/clap/latest/clap/
- https://docs.rs/clap_complete/latest/clap_complete/env/
- https://docs.rs/clap_mangen/latest/clap_mangen/
- https://rust-cli.github.io/book/tutorial/output.html
- https://rust-cli.github.io/book/tutorial/testing.html
- https://rust-cli.github.io/book/tutorial/packaging.html
- https://github.com/axodotdev/cargo-dist
- https://github.com/cargo-bins/cargo-binstall
- https://docs.rs/crossterm/latest/crossterm/
- https://docs.rs/ratatui/latest/ratatui/struct.Terminal.html
- https://docs.rs/anstream/latest/anstream/struct.AutoStream.html

## What should be built
A first credible version should ship:
1. a stack note binding together Command Surface, Terminal Surface, Runtime Settings, Distribution Contract, and Support Envelope
2. a thin aggregate artifact such as `cli-product-pack/v0` that references lower-layer packs rather than replacing them
3. one classic CLI pilot with checked help, completions, manpages, and transcript truth
4. one cargo-subcommand pilot proving Cargo-invocation identity and install posture
5. one machine-output pilot proving human-vs-machine output contracts stay explicit
6. one terminal/TUI pilot proving raw-mode, alternate-screen, color/layout/input, and cleanup truth can be attached honestly
7. one install/update/support pilot proving prebuilt/source/package-manager paths can be reviewed without folklore

The winning version is compact, boundary-aware, and consumer-friendly.
It should make tools easier to ship, support, document, and reason about without canonizing one exact crate stack.

## Initial pilots
- **Classic CLI lane** — clap help/completion/manpage/example truth
- **Cargo subcommand lane** — Cargo-native tool identity and help/invocation posture
- **Machine-output lane** — stdout/stderr/JSON/progress/quiet/verbose truth
- **Terminal/TUI lane** — raw mode, alternate screen, resize/input/layout/color/cleanup posture
- **Install/update lane** — source-build vs prebuilt vs package-manager receipts and support claims

## Milestones
1. **v0 stack and vocabulary**
   - publish the stack note and aggregate-pack shape
   - document how lower-layer artifacts compose
2. **v0.2 command pilots**
   - ship one classic CLI pilot and one cargo-subcommand pilot
   - show generated surfaces and checked examples can be attached cleanly
3. **v0.3 machine-output + terminal depth**
   - add human-vs-machine output posture and one TUI/terminal pilot
   - prove terminal truth can remain separate from parser truth
4. **v0.4 install/support depth**
   - add install receipts, fallback reasons, and support/doc imports
5. **v1 ecosystem pilots**
   - at least three materially different tools adopt the artifact family without sharing one identical parser/terminal/distribution stack

## Success metrics
- Tool authors can review what their product actually promises without reverse-engineering their own CI.
- Reviewers can tell declared command surface, live terminal behavior, configuration posture, install/update path, and support claims apart.
- Help/completion/manpage/install-snippet drift becomes diffable.
- Cargo subcommands become easier to reason about as products rather than only binaries with a naming convention.
- Support and incident work can start from portable product artifacts instead of screenshots, chat logs, and README archaeology.

## Archive fit
This proposal fills a real gap in the archive:
- **Command Surface Kit** already handles parse/help/completion/manpage truth,
- **Terminal Surface Kit** already handles terminal/input/render/layout truth,
- **Runtime Settings Kit** already handles config/env/state activation,
- **Distribution Contract Stack** already handles acquisition/install truth,
- **Support Envelope + DocProof** already handle support/docs truth.

But none of those by itself is the portable contract for **a real Rust tool as a product**.
CLI Productization Stack is the missing synthesis layer above Rust’s already powerful and already fragmented tool ecosystem.
