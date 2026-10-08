---
id: P-0531
title: CLI Surface Contract Kit — command-surface maps, output-mode receipts, terminal-posture truth, and exit-semantics witnesses
status: idea
domains: [cli, terminal, dx, tooling, automation, docs, supportiveness, output, testing]
last_reviewed: 2026-03-21
evidence:
  - https://docs.rs/clap/latest/clap/
  - https://docs.rs/clap/latest/src/clap/lib.rs.html
  - https://docs.rs/anstream/latest/anstream/struct.AutoStream.html
  - https://doc.rust-lang.org/std/io/trait.IsTerminal.html
  - https://docs.rs/indicatif/latest/indicatif/
  - https://docs.rs/dialoguer/latest/dialoguer/
  - https://doc.rust-lang.org/std/process/struct.ExitCode.html
  - https://docs.rs/trycmd/latest/trycmd/
  - https://docs.rs/snapbox/latest/snapbox/
  - https://docs.rs/assert_cmd/latest/assert_cmd/
  - https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
---

# Problem

Rust already has serious CLI substrate:

- `clap` provides argument parsing, help generation, color-choice support, value hints, shell completions, and manpage support through adjacent crates;
- `anstream` adapts styled stdout/stderr to terminal capabilities and respects color-related environment variables;
- the standard library exposes `std::io::IsTerminal` for TTY detection and `std::process::ExitCode` for process return semantics;
- `indicatif` already has a concrete non-terminal story for progress bars;
- `dialoguer` provides confirmation, input, password, fuzzy-select, editor-launch, and completion-aware prompt surfaces;
- `trycmd`, `snapbox`, and `assert_cmd` make CLI output and exit behavior testable.

What the ecosystem still lacks is one compact, reviewable answer to a downstream question that appears in every serious CLI tool:

> “What does this command actually promise on stdout, stderr, JSON mode, color, prompts, progress, and exit codes?”

Today, project docs often say some subset of:

- “built with clap”
- “supports `--json`”
- “pretty terminal output”
- “works in CI”
- “has shell completions”
- “exit code is nonzero on failure”

Those are not enough.
Another team still cannot quickly tell:

1. **which parts of the command surface are stable**;
2. **which output mode is meant for humans versus automation**;
3. **which stream owns records, diagnostics, progress, and prompts**;
4. **what changes when stdout/stderr stop being terminals**;
5. **which environment variables or runtime checks affect color and interaction**;
6. **and what each exit code class actually means**.

The missing crate is therefore **not** another parser, **not** another progress renderer, and **not** another snapshot harness.
It is a **CLI Surface Contract Kit**.

# Main judgment

A worthy crate here should provide a receiver-facing answer to:

1. **What command surface is being promised?**
   - subcommands,
   - option and positional meaning,
   - deprecation / alias posture,
   - value-hint and shell-doc coverage,
   - and stability class;
2. **What output modes exist?**
   - human text,
   - JSON,
   - JSONL,
   - table,
   - CSV,
   - or manual-review-only;
3. **What terminal posture exists?**
   - TTY detection basis,
   - color policy,
   - progress visibility,
   - prompt / editor / pager requirements,
   - and non-interactive fallback or refusal;
4. **What do exit results mean?**
   - success,
   - usage error,
   - domain-not-found,
   - partial success,
   - interrupted,
   - or manual-review-required;
5. **What belongs on stdout versus stderr?**
   - durable records,
   - diagnostics,
   - progress,
   - prompts,
   - or mixed/unstable output.

That is more useful than “uses clap + indicatif + dialoguer”.

# What it provides

- `cli-surface.toml` — maintainer-declared command/output/interaction contract, machine-readable modes, and manual-review zones.
- `command-surface.receipt.json` — command tree, stability class, aliases, deprecations, and shell-doc coverage.
- `output-mode.receipt.json` — human versus machine-readable modes, framing, schema/docs anchor, and stdout/stderr ownership.
- `terminal-mode.receipt.json` — TTY detection basis, color policy, progress posture, prompt/editor/pager posture, and non-interactive behavior.
- `exit-semantics.receipt.json` — named exit classes, portability notes, and semantic meaning.
- `cli-surface.summary.md` — short human-facing contract suitable for README / docs / support pages.
- `cli-surface-diff.report.json` — release-to-release changes in flags, output modes, terminal posture, or exit semantics.
- `cargo cli-surface init`
- `cargo cli-surface observe`
- `cargo cli-surface check`
- `cargo cli-surface doctor`
- `cargo cli-surface summary`
- `cargo cli-surface diff <old> <new>`
- `cargo cli-surface pack`

# What the crate should provide other people

1. **Automation-safe output truth** so “supports JSON” stops hiding whether JSON is stable, line-delimited, mixed with logs, or only best-effort.
2. **TTY-sensitive behavior truth** so “nice terminal output” stops hiding whether progress disappears on pipes, whether prompts require a terminal, and which color env vars matter.
3. **Exit-code meaning** so “nonzero on failure” stops hiding usage errors, empty-result states, partial success, and interrupted work.
4. **Stdout/stderr ownership truth** so machine readers know whether records, diagnostics, progress, and prompts are separated or deliberately mixed.
5. **Release diffability** so CLI contract changes become reviewable like API changes.
6. **Portable vocabulary** for comparing Cargo subcommands, developer tools, data CLIs, admin tools, and support utilities without pretending they are identical.

# Why now

This lane earns a slot now because the Rust ecosystem finally has enough substrate to make the missing layer precise.

## 1. `clap` already frames a polished CLI surface, but not a full downstream contract

The current `clap` docs and source explicitly frame a polished CLI experience with common argument behavior, help generation, suggested fixes, colored output, shell completions, and related helper/testing crates.
That is already command-surface substrate, but it is not a receiver-facing contract for stability, output modes, or exit meaning.

## 2. TTY-sensitive behavior is now explicit enough to normalize

The standard library’s `IsTerminal` trait explicitly exposes whether a handle refers to a terminal/tty, and `anstream` documents that it strips colors for non-terminals and respects `NO_COLOR` / `CLICOLOR`-style policy.
That means terminal posture is no longer folklore.
It is contract-shaped.

## 3. Progress and prompt behavior are already distinct surfaces

`indicatif` documents that progress bars draw to stderr and are completely hidden when a non-terminal is detected, while `dialoguer` documents confirmation/input/password/fuzzy-select/editor-launch surfaces.
That means a CLI can already diverge materially between operator mode and automation mode.
The missing piece is the compact receipt that tells another team where those divergences are.

## 4. Exit semantics exist, but meaning still drifts per project

The standard library’s `ExitCode` makes process return values explicit while also warning that raw numeric values are not fully portable.
That means a good crate should publish semantic exit classes instead of pretending every nonzero code says the same thing.

## 5. Test substrate exists, but not the joined support contract

`trycmd`, `snapbox`, and `assert_cmd` already make stdout/stderr/exit behavior testable.
What they do **not** do is define what part of that tested behavior another team may treat as a durable automation contract.

# Prior art scan

## `clap`
Excellent parser/help/completion/manpage substrate.
Insufficient because it still centers definition and ergonomics rather than a normalized contract for stable output, TTY posture, or exit semantics.

## `anstream`
Strong color and stream-adaptation substrate.
Insufficient because it does not publish how a given CLI divides records, diagnostics, prompts, and progress between streams and modes.

## `indicatif`
Good progress-rendering substrate with a clear non-terminal story.
Insufficient because it still does not publish a joined contract for when progress exists, where it renders, and whether it contaminates automation surfaces.

## `dialoguer`
Useful prompt/editor substrate.
Insufficient because it still does not answer whether a CLI can run unattended, what fallback it uses, or whether prompts are contractual.

## `trycmd` / `snapbox` / `assert_cmd`
Serious testing substrate.
Insufficient because tested behavior is not automatically the same as a published support contract.

## Existing app-specific `--json` modes
Often useful, sometimes excellent.
Insufficient because they are usually ad hoc, undocumented as durable contracts, and not normalized across tools.

# Recommended `0.1` first-class review objects

## `command-surface.receipt.json`

Should record at least:

- `command_family`: `single_command` | `subcommand_tree` | `cargo_subcommand` | `manual_review_required`
- `stability_class`: `stable` | `experimental` | `mixed` | `manual_review_required`
- `deprecation_posture`: `none` | `alias_only` | `warns` | `hard_removed_pending` | `manual_review_required`
- `shell_docs`: `none` | `completions_only` | `manpage_only` | `completions_and_manpages` | `manual_review_required`
- `value_hint_coverage`: `none` | `partial` | `broad` | `manual_review_required`

## `output-mode.receipt.json`

Should record at least:

- `mode_name`
- `audience`: `human` | `machine` | `mixed` | `manual_review_required`
- `encoding`: `text` | `json` | `jsonl` | `csv` | `table` | `binary` | `manual_review_required`
- `record_framing`: `whole_document` | `newline_delimited_records` | `streaming_chunks` | `not_applicable` | `manual_review_required`
- `stdout_role`: `primary_records` | `human_summary` | `mixed_unstable` | `manual_review_required`
- `stderr_role`: `diagnostics_only` | `diagnostics_and_progress` | `mixed_unstable` | `unused` | `manual_review_required`

## `terminal-mode.receipt.json`

Should record at least:

- `tty_detection_basis`: `std_is_terminal` | `crate_specific_detection` | `manual_review_required`
- `color_policy`: `never` | `auto` | `always` | `env_sensitive` | `manual_review_required`
- `progress_posture`: `none` | `stderr_tty_only` | `stdout_tty_only` | `always_visible` | `manual_review_required`
- `prompt_posture`: `none` | `tty_required` | `fallback_flags_required` | `manual_review_required`
- `editor_or_pager_posture`: `none` | `editor_optional` | `editor_required` | `pager_optional` | `manual_review_required`
- `non_interactive_behavior`: `same_surface` | `reduced_surface` | `refuse_without_override` | `manual_review_required`

## `exit-semantics.receipt.json`

Should record at least:

- `success_class`: `complete_success` | `success_with_warnings` | `manual_review_required`
- `usage_error_class`: `distinct_nonzero` | `shared_failure_code` | `manual_review_required`
- `empty_result_class`: `success` | `distinct_nonzero` | `not_applicable` | `manual_review_required`
- `partial_success_class`: `success_with_report` | `distinct_nonzero` | `not_applicable` | `manual_review_required`
- `portability_note`: `named_classes_only` | `raw_numbers_documented` | `manual_review_required`

# Commands worth shipping first

- `cargo cli-surface init`
- `cargo cli-surface observe`
- `cargo cli-surface check`
- `cargo cli-surface doctor`
- `cargo cli-surface summary`
- `cargo cli-surface diff <old> <new>`
- `cargo cli-surface pack`

# Suggested `0.1` doctor warnings

- `json_mode_missing_stdout_contract`
- `human_and_machine_modes_share_unstable_stream`
- `tty_sensitive_progress_not_declared`
- `prompt_requires_terminal_without_ci_fallback`
- `shell_docs_missing_for_stable_command_surface`
- `exit_code_numbers_documented_without_named_semantics`
- `partial_success_hidden_inside_generic_failure`

# First proving-ground scenarios

1. **Stable subcommand tree with completions and manpages**
2. **Human default mode versus JSON automation mode**
3. **Progress hidden on pipes while prompts require a TTY**
4. **Usage error versus partial success versus empty result**
5. **Color env-policy affecting human mode but not machine mode**
6. **Cargo subcommand that keeps durable records on stdout and diagnostics on stderr**

# Scope boundaries

## This proposal is not:

- another parser crate;
- another shell-completion generator;
- another TUI framework;
- another progress-bar renderer;
- another prompt widget set;
- another snapshot-test harness;
- or a claim that every CLI must adopt one exact UX style.

It is a support contract layer.

# Adoption plan

1. Start with fixture-backed contracts for `clap`-based subcommand CLIs with human and JSON modes.
2. Ship a tiny summary format maintainers can embed in `--help`, README, or docs.
3. Offer adapters for `clap`, `anstream`, `indicatif`, `dialoguer`, and common testing harness imports.
4. Publish diff reports so downstream users can review CLI contract changes across releases.
5. Let cargo subcommands, devtools, data CLIs, and admin tools import the contract rather than rewriting output/TTY/exit folklore.

# Maintenance plan

- Keep the core vocabulary intentionally small.
- Prefer explicit `manual_review_required` over pretending unstable CLI behavior is solved.
- Version the JSON schemas conservatively.
- Treat stream ownership and exit semantics as durable review objects, not snapshot accidents.
- Track ecosystem evolution, but keep parser/help/prompt/progress/testing crates as import substrate rather than dependencies of the concept.

# Why this could matter

This is the crate that would let maintainers say:

- “This CLI’s JSONL stream is the automation contract; the human summary is not.”
- “Progress only appears on stderr when a terminal is present.”
- “Interactive confirmation requires a TTY and the non-interactive path must use `--yes`.”
- “`no matches` is success for scripting, not a generic failure.”
- “Usage errors, partial success, and interrupted execution are separate exit classes.”

That is a real missing support layer in Rust today.
