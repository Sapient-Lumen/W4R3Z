# Gap: command surfaces and CLI contracts

## What is missing
Rust has strong CLI building blocks, but it still lacks a **shared command-surface contract**.

Today there is no standard way to describe, exchange, and diff:
- which subcommands, flags, arguments, external subcommand lanes, and help/manpage/completion surfaces a CLI intends to support,
- which shells, platforms, and installation modes those generated surfaces assume,
- which command examples are treated as executable promises versus illustrative prose,
- which exit-code families, stderr/help conventions, and completion artifacts were actually checked,
- and what evidence came back from CLI-focused tests.

That missing layer matters because Rust is one of the ecosystems where command-line tools and `cargo-*` subcommands are a first-class product category, not a side hobby.

Sources:
- https://docs.rs/clap
- https://doc.rust-lang.org/cargo/reference/external-tools.html
- https://docs.rs/clap/latest/clap/struct.Command.html
- https://docs.rs/clap/latest/clap/enum.ValueHint.html
- https://docs.rs/clap_complete/
- https://docs.rs/clap_complete/latest/clap_complete/env/index.html
- https://docs.rs/clap_mangen
- https://docs.rs/assert_cmd
- https://docs.rs/trycmd
- https://docs.rs/snapbox
- https://rust-cli.github.io/book/tutorial/testing.html

## The current seam is awkward
The ecosystem has real building blocks:
- `clap` provides a structured command model and explicitly aims for a polished CLI experience with help generation, suggestions, colored output, and shell completions,
- `clap::Command` already describes arguments, subcommands, parser behavior, and help output,
- `ValueHint` lets authors communicate completion semantics to shells,
- `clap_complete` generates shell completions,
- `clap_mangen` generates man pages from the same command model,
- `assert_cmd` simplifies CLI integration testing,
- `trycmd` and `snapbox` cover transcript-style and specialized snapshot testing,
- and the Rust CLI book explicitly treats CLI testing as more than ordinary function-level assertions.

But each real project still hand-assembles its command surface out of:
- parser definitions,
- generated `--help` text,
- shell completion scripts,
- man pages,
- README or guide transcripts,
- integration tests,
- snapshot baselines,
- and CI jobs that only maintainers know how to interpret.

The result is not that Rust lacks parser or test crates.
The result is that there is no portable way to say:
- “this is the declared command surface and support envelope,”
- “these generated help/man/completion artifacts are part of the shipped interface,”
- “these transcript examples were actually checked,”
- or “these shell/platform lanes are advisory versus supported.”

Sources:
- https://docs.rs/clap
- https://docs.rs/clap/latest/clap/struct.Command.html
- https://docs.rs/clap/latest/clap/enum.ValueHint.html
- https://docs.rs/clap_complete/
- https://docs.rs/clap_complete/latest/clap_complete/env/index.html
- https://docs.rs/clap_mangen
- https://docs.rs/assert_cmd
- https://docs.rs/trycmd
- https://docs.rs/snapbox
- https://rust-cli.github.io/book/tutorial/testing.html

## Why this matters
This gap is bigger than “nicer help text.”
It affects:
1. **command UX stability** — parser changes, help text, completion hints, and man pages all form user-visible interfaces;
2. **installation and shell support** — generated completion artifacts can drift from the binary, and `clap_complete` explicitly warns that dynamic completion interfaces can mismatch across upgrades;
3. **documentation truthfulness** — transcript examples in READMEs, books, and docs are often the most concrete user promises, but their results stay trapped in repo-local harnesses;
4. **Cargo subcommand ecosystems** — Cargo’s external-tool model means many Rust tools are extensions of the main developer workflow rather than isolated binaries;
5. **release review and archaeology** — teams often cannot answer which command behaviors were intended, generated, tested, or merely demonstrated in prose.

Sources:
- https://docs.rs/clap
- https://docs.rs/clap_complete/latest/clap_complete/env/index.html
- https://docs.rs/trycmd
- https://docs.rs/assert_cmd
- https://rust-cli.github.io/book/tutorial/testing.html
- https://doc.rust-lang.org/cargo/reference/external-tools.html

## What “good” looks like
A worthy contribution here is **not** another argument parser, another shell-completion crate, or another snapshot runner.

It is a shared command-surface boundary:
- one `command-surface/v0` describing subcommands, arguments, generated UX surfaces, shell/platform assumptions, and support levels,
- one `command-example-catalog/v0` inventorying checked transcripts, help snapshots, completion fixtures, and illustrative-only examples,
- one `command-check-plan/v0` declaring which validators should run against which command surfaces,
- one `command-check-report/v0` recording what passed, failed, drifted, or was skipped,
- and one `command-pack/v0` bundle for CI, release review, documentation, installers, and long-term archaeology.

That would let DocProof Kit, Release Pipeline Kit, Support Envelope Kit, `cargo-*` subcommand authors, and future CLI frameworks talk about the same command-support story instead of scattering the truth across generated files and local tests.
