# Design: Command Surface Kit (`cargo cmdcheck`, `command-pack/v0`)

## Goal
Define a portable contract for declaring, generating, checking, diffing, and reviewing Rust CLI surfaces: parser shape, help/manpage/completion outputs, transcript examples, shell assumptions, and behavioral evidence.

This should **not** replace `clap`, shell-completion generators, snapshot-testing crates, or the Rust CLI book.
It should make them compose better and make command-support claims reviewable.

## References (signals)
- `clap` explicitly aims to give users a polished CLI experience, including common argument behavior, help generation, suggested fixes, colored output, and shell completions.
  https://docs.rs/clap
- `clap::Command` already models arguments, subcommands, parser behavior, and help output.
  https://docs.rs/clap/latest/clap/struct.Command.html
- `ValueHint` already carries completion semantics to shells.
  https://docs.rs/clap/latest/clap/enum.ValueHint.html
- `clap_complete` supports compile-time and runtime completion generation.
  https://docs.rs/clap_complete/
- `clap_complete` also documents that dynamic completion interfaces can mismatch with the program after upgrades, which is strong evidence that completions are a versioned support surface.
  https://docs.rs/clap_complete/latest/clap_complete/env/index.html
- `clap_mangen` generates man-page source from a `clap::Command`.
  https://docs.rs/clap_mangen
- `assert_cmd` exists specifically to simplify integration testing of CLIs.
  https://docs.rs/assert_cmd
- `trycmd` provides bulk snapshot testing for command transcripts, while `snapbox` covers more customized one-off cases.
  https://docs.rs/trycmd
  https://docs.rs/snapbox
- The Rust CLI book’s testing chapter highlights that CLI programs involve user input, files, and output, which makes them broader than ordinary function-level tests.
  https://rust-cli.github.io/book/tutorial/testing.html
- Cargo external tools mean `cargo-*` subcommands are a first-class extension surface in Rust.
  https://doc.rust-lang.org/cargo/reference/external-tools.html

## Core components

### 1) `command-surface/v0`
A design-time declaration of what command interface a crate/workspace/release is claiming to support.

Required ideas:
- subject identity (crate / workspace / installed binary / cargo subcommand)
- command graph:
  - command name
  - subcommands
  - external-subcommand lanes when relevant
- argument metadata:
  - option/flag/positional identities
  - value shape and hints
  - deprecation / hidden / experimental markers
- generated-surface declarations:
  - `--help` / `-h`
  - shell completions
  - man pages
  - long-version / build-info surfaces when relevant
- shell/platform assumptions:
  - supported shells for completions
  - platform-specific command differences
  - support level (`official`, `best-effort`, `experimental`, `docs-only`, `deprecated`)
- output/behavior policy:
  - expected exit-code families
  - stdout/stderr stability posture
  - color / tty assumptions when relevant
- attachment policy for CI/release/docs/installers

Design rule: **command-surface declarations must separate parser shape, generated surfaces, and checked behavior**.
Passing a transcript test is not the same thing as declaring an interface.

### 2) `command-example-catalog/v0`
An inventory of executable and illustrative command examples.

Should record:
- source location (README, mdBook, docs.rs example, test fixture, manpage example, help snapshot)
- command invocation form
- environment / filesystem / fixture assumptions
- expected output mode (`stdout`, `stderr`, `help`, `version`, `completion`, `manpage`)
- whether the example is:
  - `checked-transcript`
  - `checked-help`
  - `checked-completion`
  - `checked-manpage`
  - `illustrative-only`
- links to supporting harnesses (`assert_cmd`, `trycmd`, `snapbox`, handwritten test)

This is the missing answer to “which command examples are promises versus prose?”

### 3) `command-check-plan/v0`
A machine-readable plan for how a command surface will be validated.

Should record:
- linked `command-surface/v0`
- selected command/example coverage
- shell/platform lanes to run
- generation steps (help, completion, manpage)
- validators chosen (`assert_cmd`, `trycmd`, `snapbox`, custom)
- normalization policy (paths, colors, timestamps, platform-specific wording)
- skip/waiver reasons such as:
  - `shell-not-available`
  - `platform-specific-output`
  - `interactive-flow-unsupported`
  - `dynamic-completion-not-stable`
  - `illustrative-only-example`

### 4) `command-check-report/v0`
Machine-readable evidence for what command surfaces were actually checked.

Should record:
- linked plan and surface declarations
- generated artifacts produced (help, completions, man pages)
- transcript/help/version/completion/manpage results
- observed exit-code families and mismatch reasons
- drift reason codes such as:
  - `help-text-drift`
  - `completion-script-drift`
  - `manpage-drift`
  - `stderr-contract-drift`
  - `exit-code-mismatch`
  - `shell-support-gap`
  - `platform-output-gap`
  - `example-unchecked`
- raw attachment pointers (generated files, snapshots, transcript fixtures, normalized outputs)

This is the missing answer to “what parts of the CLI surface did we really validate?”

### 5) `command-pack/v0`
Bundle format containing:
- `command-surface/v0`
- optional `command-example-catalog/v0`
- optional `command-check-plan/v0`
- one or more `command-check-report/v0`
- optional diff reports and raw attachments

This is the unit that should travel through CI, release review, docs, shell-install scripts, and later archaeology.

### 6) `cargo cmdcheck`
Reference UX:
- `cargo cmdcheck init`
- `cargo cmdcheck generate`
- `cargo cmdcheck check`
- `cargo cmdcheck diff`
- `cargo cmdcheck pack`

`cargo cmdcheck` should begin as an explainer / adapter / packer.
It should not pretend to be the one true parser framework or a hosted snapshot service.

## Default policy
- **Separate declared interface from observed behavior.**
- **Treat generated help/completions/manpages as first-class surfaces** instead of disposable build products.
- **Record shell and platform assumptions explicitly** rather than hiding them in install snippets or issue comments.
- **Preserve raw source truth** for generated artifacts and snapshot fixtures.
- **Distinguish checked transcripts from illustrative examples** so docs can be honest.

## What the kit should provide to others
- **DocProof Kit:** consume command examples and checked transcripts without owning parser/help/completion semantics.
- **Release Pipeline Kit:** attach command packs to binary releases and installer bundles.
- **Support Envelope Kit:** relate shell/platform support claims to broader platform support envelopes.
- **Config Set Kit:** choose bounded CLI check matrices (shells, targets, interactive modes) without redefining the command contract.
- **ScriptKit:** reuse command-surface and check-report artifacts for single-file tools that still ship real CLI promises.
- **Cargo subcommand authors:** expose user-facing command surfaces in a portable way instead of leaving them buried in snapshots and READMEs.

## Overlap boundaries
- **Not `clap`:** `clap` is a parser and command-model framework; this kit packages interface declarations and evidence across frameworks and generated surfaces.
- **Not DocProof Kit:** DocProof verifies learning/documentation surfaces broadly; this kit focuses on the operational command interface itself.
- **Not Release Pipeline Kit:** release tooling ships artifacts; this kit explains and validates the command UX those artifacts expose.
- **Not Support Envelope Kit:** support envelopes describe where something runs; this kit describes what command interface is promised on those surfaces.
- **Not another snapshot framework:** the value is the portable artifact and review workflow, not a new assertion DSL.

## Hard problems (explicitly scoped)
1. **CLI surfaces are partly generated**
   - help text, completions, and man pages often derive from parser definitions.
   - v0 must preserve both the declared source and the generated outputs.

2. **Behavior stability is contextual**
   - some output is contract-grade, some is best-effort, some is interactive or shell-dependent.
   - reports must allow honest partial guarantees.

3. **Shell support is messy**
   - completions differ by shell, generation mode, and installation path.
   - v0 should model explicit support levels instead of pretending all generated completions are equal.

4. **CLI docs and CLI behavior overlap but are not identical**
   - README/manpage/help/transcript examples often describe the same tool from different angles.
   - the kit should connect them without erasing the distinction.

5. **Cargo subcommands complicate identity**
   - the installed binary name, `cargo <subcommand>` invocation, and standalone invocation may differ.
   - the contract must preserve both identities when relevant.

## Minimal adoption path
1. Publish schemas + validators for `command-surface/v0` and `command-check-report/v0`.
2. Ship `cargo cmdcheck generate` and `cargo cmdcheck check` first.
3. Ingest `clap` metadata, generated help, `clap_complete` outputs, and `clap_mangen` outputs where available.
4. Add adapters for `assert_cmd`, `trycmd`, and `snapbox` fixtures.
5. Add diff/report support so release and docs workflows can review command-surface drift directly.

## Why this is an ecosystem contribution, not just repo hygiene
Rust already has enough CLI-specific tooling that a missing shared command contract is now the real bottleneck.
A portable command-surface artifact would make Rust CLI projects easier to review, easier to ship, easier to document honestly, and easier to maintain across shells, subcommands, and installation paths.
That is a substrate contribution, not a convenience wrapper.
