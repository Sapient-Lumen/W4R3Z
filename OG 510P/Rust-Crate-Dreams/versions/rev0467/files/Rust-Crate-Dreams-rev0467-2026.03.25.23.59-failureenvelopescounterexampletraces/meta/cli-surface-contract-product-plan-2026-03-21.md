# CLI Surface Contract Kit — product plan (2026-03-21)

This note sharpens **P-0531 CLI Surface Contract Kit** into an implementation-ready `0.1` shape.

## Core question

If somebody started building **P-0531** this week, what should version `0.1` look like, what should it provide other people, and what should be left for later?

## Main judgment

The first implementation should not try to replace parser crates, standardize every UX choice, or prove full output stability for every CLI.
It should provide one boring, reviewable contract layer above today’s Rust CLI substrate.

`0.1` should make four things first-class:

1. **command surface** — command tree, stability posture, aliases/deprecations, and shell-doc coverage;
2. **output mode** — human versus machine-readable surfaces, encoding/framing, and stdout/stderr ownership;
3. **terminal posture** — TTY detection, color policy, progress posture, prompting, and editor/pager handoff;
4. **exit semantics** — success/failure classes and what nonzero outcomes actually mean.

## What `0.1` should provide other people

- one compact `command-surface.receipt.json`
- one compact `output-mode.receipt.json`
- one compact `terminal-mode.receipt.json`
- one compact `exit-semantics.receipt.json`
- one rendered `cli-surface.summary.md`
- a diff command for release reviewers

## Commands worth shipping first

- `cargo cli-surface init`
- `cargo cli-surface observe`
- `cargo cli-surface check`
- `cargo cli-surface doctor`
- `cargo cli-surface summary`
- `cargo cli-surface diff <old> <new>`
- `cargo cli-surface pack`

## What to import, not reinvent

- `clap` command metadata and shell-doc substrate
- `anstream` / `anstyle_query` color and stream-adaptation substrate
- `std::io::IsTerminal`
- `indicatif` progress posture
- `dialoguer` prompt/editor posture
- `trycmd`, `snapbox`, and `assert_cmd` for observed scenario evidence

## Suggested `0.1` doctor warnings

- `stable_command_surface_missing_shell_docs`
- `machine_mode_missing_stream_contract`
- `human_and_machine_output_not_separated`
- `tty_sensitive_progress_not_declared`
- `prompt_requires_terminal_without_override_recipe`
- `exit_semantics_missing_named_classes`
- `partial_success_or_empty_result_undocumented`

## First proving-ground scenarios

1. **Stable subcommand tree with completions and manpages**
2. **Human default output versus JSON automation mode**
3. **Progress hidden on non-terminals**
4. **Interactive prompt requiring TTY or explicit override**
5. **Usage error versus partial success exit meaning**
6. **Cargo subcommand with stdout records and stderr diagnostics**

## What to leave for later

- full shell UX standardization
- localization / rich formatting beyond basic output-mode declaration
- transcript rendering and terminal screenshot tooling
- TUI/full-screen app contracts
- pager/editor lifecycle deep dives
- static proof that every output byte is stable across all versions
