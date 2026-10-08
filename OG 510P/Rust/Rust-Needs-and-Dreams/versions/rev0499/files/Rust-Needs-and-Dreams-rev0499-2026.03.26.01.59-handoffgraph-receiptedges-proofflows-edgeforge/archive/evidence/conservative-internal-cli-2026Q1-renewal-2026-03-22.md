# Renewal receipt: conservative internal CLI / automation (2026-03-22)

## Subject
- default card: `defaults/conservative-internal-cli-2026Q1.md`
- review date: 2026-03-22
- archive revision: rev0380
- scope: conservative internal CLI / automation for stable Rust, ordinary Cargo workflows, workstation + CI use
- non-goal: package-admission signoff for a specific project dependency set

## Renewal verdict
**keep**

The lane still reads correctly as:
- `clap` for parser ergonomics and canonical documentation,
- `serde` for typed config/data interchange,
- `tracing` + `tracing-subscriber` for diagnostics,
- `anyhow` at the binary boundary,
- `thiserror` for structured internal error types,
with `argh` and `color-eyre` still visible as serious alternatives rather than hidden losers.

No lane-level split is required yet, though future revisions may sharpen the boundary between **internal automation** and **consumer-facing CLI**.

## Canon import checked this round
Primary documentation surfaces re-read:
- Clap overview and derive tutorial:
  https://docs.rs/clap/latest/clap/
  https://docs.rs/clap/latest/clap/_derive/_tutorial/index.html
- `argh` overview:
  https://docs.rs/argh/latest/argh/
- Serde:
  https://serde.rs/
  https://serde.rs/derive.html
- `tracing-subscriber` formatting and filtering:
  https://docs.rs/tracing-subscriber/latest/tracing_subscriber/fmt/
  https://docs.rs/tracing-subscriber/latest/tracing_subscriber/filter/struct.EnvFilter.html
- `anyhow`:
  https://docs.rs/anyhow/latest/anyhow/
- `thiserror`:
  https://docs.rs/thiserror/latest/thiserror/
- `color-eyre`:
  https://docs.rs/color-eyre/latest/color_eyre/

Canon judgment:
- the canonical surfaces remain strong and unusually teachable for this project class;
- the current default continues to win more on **boring legibility and documentation** than on novelty.

## Registry / supply-chain import
Public ecosystem signals checked:
- crates.io development update:
  https://blog.rust-lang.org/2026/01/21/crates-io-development-update/
- RustSec advisories:
  https://rustsec.org/advisories/

What this receipt takes from those sources:
- Security-tab advisory surfacing now belongs in renewal hygiene.
- Trusted Publishing only mode, SLOC, source browsing links, and `pubtime` make public review better than it used to be.
- Recent malicious lookalike removals (`oncecell`, `serd`, `envlogger`, and others) are a concrete warning against fuzzy package naming.

Exact identity notes for this lane:
- `clap` is **not** “clapp” or a generic parser family label.
- `serde` is **not** `serd`.
- `tracing-subscriber` should be named exactly, not merely “tracing utils”.
- `anyhow` / `thiserror` / `argh` / `color-eyre` should be preserved as exact crate identifiers.

Registry judgment:
- this receipt does **not** assert that the named crates are universally admitted or free of future advisories;
- it asserts that public review surfaces are now good enough that lane renewal should preserve exact identity and expect real registry checks at renewal time.

## API / compatibility import
Relevant current signals:
- Cargo unstable/reference surface:
  https://doc.rust-lang.org/cargo/reference/unstable.html
- Cargo changelog (`--publish-time`):
  https://doc.rust-lang.org/cargo/CHANGELOG.html
- `cargo-semver-checks` goal:
  https://rust-lang.github.io/rust-project-goals/2025h2/cargo-semver-checks.html

Judgment:
- nothing in the current lane requires a changed lane-level answer on compatibility grounds;
- the ecosystem is improving its compatibility/replay tooling, but the CLI lane still lives mostly at the application level, not at a public library API boundary where semver machinery alone would decide the answer.

## Maintenance / support-envelope import
Support-envelope facts that still hold:
- stable Rust is the intended posture;
- non-`no_std`, workstation + CI environments remain the dominant fit;
- mixed-experience teams still benefit from a parser/logging/error lane with strong docs and low surprise.

Maintenance judgment:
- no new evidence suggests this lane should be replaced by a more novelty-driven stack;
- the conservative/internal framing still matters, and the card should keep that framing explicit.

## Freshness / replay notes
Fresh inputs checked on 2026-03-22:
- Rust challenges post:
  https://blog.rust-lang.org/2026/03/20/rust-challenges/
- 2025 State of Rust survey:
  https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- crates.io development update:
  https://blog.rust-lang.org/2026/01/21/crates-io-development-update/
- RustSec advisories:
  https://rustsec.org/advisories/

Replay notes:
- future renewal should explicitly re-check per-crate Security tabs and current registry posture;
- if `cargo-semver-checks`, `--publish-time`, or other replay surfaces become easier to consume, add them as explicit receipt attachments rather than rewriting the prose.

## Lane judgment
Keep the lane.

Why:
- CLI remains one of Rust’s strongest domains;
- the problem is still choosing a sane, teachable default rather than finding any library at all;
- this lane remains a good conservative answer for internal tooling without pretending to bless all CLIs.

## Open watch items
- whether internal automation and consumer-facing CLI should become separate maintained cards;
- whether richer operator-facing diagnostics (`color-eyre`) deserve a promoted sub-lane instead of staying an optional embellishment;
- whether exact-identity hygiene should graduate from note-level discipline into a machine-checked receipt schema.
