# Gap: CLI tools, terminal apps, and cargo-subcommand productization contracts

## What is missing
Rust has a strong command-line and terminal ecosystem, but it still lacks a **portable productization layer for real tools**.

Today there is no shared way to publish, exchange, and diff:
- the declared command surface of a tool (subcommands, flags, completions, man pages, machine-readable modes, cargo-subcommand identity),
- the live terminal semantics it expects (TTY assumptions, color policy, raw mode, alternate screen, resize/input behavior, Unicode layout),
- the runtime settings and activation posture it relies on (config files, env vars, profiles, cache/data locations, credentials when relevant),
- the install/update/acquisition paths users actually take (source build, prebuilt binary, package-manager path, mirror/fallback path),
- and the support/docs claims that tell users which shells, platforms, and interaction modes are really supported.

That missing layer matters because Rust is now good enough at tools that the problem is no longer “can Rust make a CLI?”
The problem is “how does a Rust tool become a reviewable product instead of a pile of parser definitions, terminal assumptions, release artifacts, and README folklore?”

## The current seam is awkward
Rust already has strong ingredients, but they stop short of a shared product boundary:
- `clap` already models command graphs, argument semantics, help/version surfaces, and related generators/tests;
- `clap_complete` and `clap_mangen` make completions and manpages first-class generated surfaces;
- Cargo custom subcommands make `cargo-*` tools a native ecosystem lane rather than an external curiosity;
- the Rust CLI book explicitly treats output policy, testing, packaging, and distribution as part of serious tool design;
- `cargo-dist` and `cargo-binstall` prove release/install/distribution is already a distinct concern above `cargo install`;
- `crossterm`, Ratatui, `anstream`, and adjacent terminal crates prove that terminal/runtime semantics are their own layer rather than parser trivia;
- and the 2025H2 `cargo script` goal says Rust is actively trying to make small utilities and reproducible bug reports more natural, which expands the tool-shaped surface area even further.

So the ecosystem is not missing one more parser crate, one more shell-completion crate, one more TUI framework, or one more installer wrapper.
It is missing the **boring contract/evidence layer that keeps command truth, terminal truth, runtime-setting truth, install truth, and support truth distinct while still letting them compose**.

## Why this matters
This gap matters because it hits multiple real Rust tool families at once:
1. **ordinary CLIs** — help/completions/manpages/output modes/install paths are user-facing interfaces, not implementation details;
2. **cargo subcommands** — identity, help forwarding, package/install posture, and Cargo-integration assumptions become part of the product contract;
3. **terminal-first tools and TUIs** — raw mode, alternate screen, color/layout/input semantics, and cleanup guarantees shape whether the tool is actually usable;
4. **machine-facing operator tools** — stdout/stderr/JSON/progress behavior and quiet/verbose modes affect scripting and CI reliability;
5. **support/release archaeology** — teams often cannot later answer what was declared, what was generated, what was tested, what was shipped, and what was merely demonstrated in docs.

A worthy contribution here is therefore not “a better CLI framework.”
It is a shared way to make **Rust tools legible as products**.

## What “good” looks like
A worthy contribution here is **not** another giant abstraction crate.
It is a thin stack above the existing pieces:
- **Command Surface Kit** for parser/help/completion/manpage and cargo-subcommand identity truth,
- **Terminal Surface Kit** for TTY/raw-mode/color/layout/input/render truth,
- **Runtime Settings Kit** for config/env/cache/profile/activation truth,
- **Distribution Contract Stack** for source-vs-prebuilt-vs-package-manager selection, verification, fallback, and install receipts,
- **Support Envelope + DocProof** for shell/platform/runtime/support/docs truth,
- and one thin aggregate artifact such as `cli-product-pack/v0` that references those lower-layer artifacts instead of erasing them.

That would let release tooling, installers, docs, support, incident review, ecosystem atlas work, and future LLM/editor consumers talk about the **same tool** without scraping README snippets and CI logs.

## Sources
- https://rust-lang.github.io/rust-project-goals/
- https://doc.rust-lang.org/cargo/reference/external-tools.html
- https://docs.rs/clap/latest/clap/
- https://docs.rs/clap_complete/latest/clap_complete/env/
- https://docs.rs/clap_mangen/latest/clap_mangen/
- https://rust-cli.github.io/book/tutorial/testing.html
- https://rust-cli.github.io/book/tutorial/packaging.html
- https://rust-cli.github.io/book/tutorial/output.html
- https://github.com/axodotdev/cargo-dist
- https://github.com/cargo-bins/cargo-binstall
- https://docs.rs/crossterm/latest/crossterm/
- https://docs.rs/ratatui/latest/ratatui/struct.Terminal.html
- https://docs.rs/anstream/latest/anstream/struct.AutoStream.html
