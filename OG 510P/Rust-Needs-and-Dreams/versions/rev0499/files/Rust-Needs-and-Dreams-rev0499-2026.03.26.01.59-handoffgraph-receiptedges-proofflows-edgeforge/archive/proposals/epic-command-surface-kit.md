# Epic proposal: Command Surface Kit

## Thesis
Rust already has serious CLI building blocks.
The next high-leverage contribution is not another parser or another snapshot-testing crate.
It is a **shared command-surface layer** that turns parser shape, generated help/completions/manpages, transcript examples, and behavioral evidence into durable engineering artifacts.

That would be a worthy ecosystem contribution because it helps:
- CLI authors treat `--help`, shell completions, man pages, and transcripts as first-class release surfaces,
- Cargo subcommand maintainers review interface drift without diffing generated files by hand,
- documentation and release tooling share the same truth about command examples,
- and downstream packagers stop reverse-engineering shell/install assumptions from READMEs and CI snippets.

## Why now
The timing is good because Rust already has the ingredients, but still not the contract:
- `clap` already models commands and explicitly aspires to polished CLI UX;
- `clap_complete` and `clap_mangen` already generate major user-facing surfaces from that model;
- `assert_cmd`, `trycmd`, and `snapbox` already cover much of the testing story;
- the Rust CLI book already frames CLI behavior as broader than ordinary unit tests;
- and Cargo external tools mean command-line extensions are a major Rust product category.

Sources:
- https://docs.rs/clap
- https://docs.rs/clap/latest/clap/struct.Command.html
- https://docs.rs/clap_complete/
- https://docs.rs/clap_complete/latest/clap_complete/env/index.html
- https://docs.rs/clap_mangen
- https://docs.rs/assert_cmd
- https://docs.rs/trycmd
- https://docs.rs/snapbox
- https://rust-cli.github.io/book/tutorial/testing.html
- https://doc.rust-lang.org/cargo/reference/external-tools.html

## Proposed shape
Ship a narrowly scoped reference stack:
1. schemas for `command-surface/v0`, `command-example-catalog/v0`, `command-check-plan/v0`, `command-check-report/v0`, and `command-pack/v0`
2. adapters for `clap` command definitions, generated help/completion/manpage artifacts, and transcript/snapshot harnesses
3. explicit reporting for weak spots (`interactive-flow-unsupported`, `shell-support-gap`, `illustrative-only`, `dynamic-completion-not-stable`)
4. CI and release examples showing command packs attached to docs, installers, and binary releases
5. guidance for preserving raw generated artifacts and transcript fixtures instead of flattening everything into one fake canonical CLI spec

The winning version is boring, adapter-heavy, and explicit about shell/platform assumptions.
It should make today’s crates legible together rather than replacing them.

## Initial pilots
- one `cargo-*` subcommand with generated completions and man pages
- one standalone developer tool using `clap` + `trycmd` + `assert_cmd`
- one multi-command CLI that ships both docs/book transcripts and packaged completion scripts
- one script-like Rust utility that still wants a durable command contract for packaging and support

## Milestones
1. **v0 artifacts + docs**
   - publish schemas and examples
   - preserve command source truth, generated surfaces, and transcript provenance
2. **v0.2 adapters**
   - support `clap`, `clap_complete`, `clap_mangen`, `assert_cmd`, `trycmd`, and `snapbox`
   - capture shell/platform assumptions honestly
3. **v0.3 cross-kit integration**
   - integrate with DocProof, Release Pipeline, Support Envelope, and Config Set artifacts
   - support baseline/diff workflows across releases and installer changes
4. **v1 ecosystem pilots**
   - at least three materially different adopters use the schemas without sharing one exact testing or packaging setup

## Success metrics
- Teams can review CLI changes as explicit interface and evidence artifacts rather than giant snapshot diffs and issue comments.
- Generated help, completion, and manpage drift becomes visible instead of incidental.
- Transcript examples become attachable evidence rather than repo-local folklore.
- Cargo subcommands and standalone binaries can describe their support surfaces in one portable form.
- Rust release, documentation, and installer workflows can point to a durable command pack.

## Archive fit
This proposal adds an underrepresented but important domain to the concise archive: **command-line application maturity and CLI UX contracts**.
It also fills a deliberate hole left by DocProof Kit, which includes transcripts as one documentation surface but does not try to become the command-interface contract for binaries and Cargo subcommands themselves.
Command Surface Kit is the missing CLI-specific substrate that can travel alongside docs, releases, support envelopes, and script workflows without being absorbed by any of them.
