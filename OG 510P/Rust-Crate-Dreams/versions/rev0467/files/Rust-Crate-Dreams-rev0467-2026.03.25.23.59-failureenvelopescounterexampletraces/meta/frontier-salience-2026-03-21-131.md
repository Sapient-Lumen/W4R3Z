# Frontier salience snapshot — 2026-03-21 (131)

This pass did **not** promote another parser crate, another progress renderer, or another prompt toolkit.
It added **P-0531 CLI Surface Contract Kit** because the archive still lacked one receiver-facing layer above Rust’s command-line substrate.

## Main judgment

The sharper missing layer is not “how do I parse flags?” and not “which CLI helper stack should I install?”.
The sharper missing layer is a **CLI support contract** that publishes:

- what the durable command surface is,
- which output mode is for automation,
- what changes when a TTY disappears,
- and what exit outcomes actually mean.

## Why this moved now

Current Rust CLI substrate already makes the problem precise:

1. `clap` already frames a polished CLI surface with help, color, value hints, completions, and adjacent testing/documentation crates.
2. `anstream` already adapts styled stdout/stderr to terminal capabilities and color env vars.
3. `std::io::IsTerminal` makes TTY detection explicit enough to normalize.
4. `indicatif` already makes progress visibility differ between terminals and non-terminals.
5. `dialoguer` already makes prompt/editor behavior a first-class runtime surface.
6. `std::process::ExitCode` already makes exit semantics explicit while warning against naive raw-code portability.
7. `trycmd`, `snapbox`, and `assert_cmd` already make stdout/stderr/exit behavior testable.

## Why this beat nearby work

The archive already had adjacent lanes for:

- example / first-success support,
- test-surface support,
- guidance / diagnostics,
- diagnosis bundles,
- and broader product-engineering work.

What it still lacked was one compact way to say:

- “this JSON mode is the automation contract; the default text mode is not,”
- “progress appears only on stderr when a terminal exists,”
- “interactive confirmation requires a TTY or an explicit override flag,”
- “stdout owns durable records while stderr owns diagnostics,”
- and “usage error, partial success, and empty result are not one generic failure class.”

That is a real crate contribution, not just another CLI article.

## Broad portfolio ranking after this pass

1. **P-0509 Crate Ecosystem Pathfinder & Decision-Pack Kit**
2. **P-0514 Crate Upgrade Pack Kit**
3. **P-0520 Crate Lifecycle Surface Pack Kit**
4. **P-0531 CLI Surface Contract Kit**
5. **P-0529 Channel Surface Contract Kit**
6. **P-0530 Request Execution Policy Contract Kit**
7. **P-0523 Crate Test Surface Pack Kit**
8. **P-0518 Crate Observability Surface Pack Kit**
9. **P-0528 Cargo Feature Surface Contract Kit**
10. **P-0474 Cargo Config Layer Receipt Kit**

## What changed in the archive

Added:
- `entries/2026-03-21-311.md`
- `meta/frontier-salience-2026-03-21-131.md`
- `meta/cli-surface-contract-product-plan-2026-03-21.md`
- `meta/cli-surface-contract-lane-boundaries-2026-03-21.md`
- `proposals/cli-surface-contract-kit.md`
- `fixtures/cli-surface-contract-kit/README.md`
- `command-surface` / `output-mode` / `terminal-mode` / `exit-semantics` schemas
- scenario families for command-surface shell docs, human-vs-JSON mode separation, TTY-sensitive progress/prompt posture, and exit-class separation

Updated:
- `README.md`
- `INDEX.md`
- `meta/prioritization.md`
- `meta/roadmap.md`
- `meta/research-ledger.md`
- `meta/decision-log.md`
- `meta/llm-hygiene.md`

## Freshness anchors

- `clap` docs — https://docs.rs/clap/latest/clap/
- `clap` source aspirations — https://docs.rs/clap/latest/src/clap/lib.rs.html
- `anstream::AutoStream` docs — https://docs.rs/anstream/latest/anstream/struct.AutoStream.html
- `std::io::IsTerminal` docs — https://doc.rust-lang.org/std/io/trait.IsTerminal.html
- `indicatif` docs — https://docs.rs/indicatif/latest/indicatif/
- `dialoguer` docs — https://docs.rs/dialoguer/latest/dialoguer/
- `std::process::ExitCode` docs — https://doc.rust-lang.org/std/process/struct.ExitCode.html
- `trycmd` docs — https://docs.rs/trycmd/latest/trycmd/
- `snapbox` docs — https://docs.rs/snapbox/latest/snapbox/
- `assert_cmd` docs — https://docs.rs/assert_cmd/latest/assert_cmd/
