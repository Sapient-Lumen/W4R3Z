# Renewal receipt: script / repro / tiny utility (2026-03-22)

## Subject
- default card: `defaults/script-repro-tiny-utility-2026Q1.md`
- review date: 2026-03-22
- archive revision: rev0380
- scope: single-purpose scripts, repros, teaching snippets, and tiny utilities where one-file shareability is part of the value
- non-goal: blessing single-file packages as the default for normal long-lived applications

## Renewal verdict
**keep with caveats**

The lane still reads correctly as:
- single `.rs` file,
- embedded manifest/frontmatter when dependencies are needed,
- `cargo script` / single-file package flow,
- escalation to an ordinary Cargo package when growth starts.

The default remains intentionally weaker than the CLI/service cards because the workflow still depends on unstable Cargo support as of this review.

## Canon import checked this round
Primary official surfaces re-read:
- cargo-script project goal:
  https://rust-lang.github.io/rust-project-goals/2024h2/cargo-script.html
- Project goals for 2025H2:
  https://blog.rust-lang.org/2025/10/28/project-goals-2025h2/
- Rust in 2026 / flagships:
  https://rust-lang.github.io/rust-project-goals/2026/flagships.html
- Program-management update:
  https://blog.rust-lang.org/inside-rust/2026/02/11/program-management-update-2026-01/
- Cargo unstable feature reference:
  https://doc.rust-lang.org/cargo/reference/unstable.html

Canon judgment:
- official momentum for single-file packages remains real;
- the communication/repro/teaching use case is still clearly endorsed;
- but the unstable/reference posture still justifies `default-with-caveats`, not a stable universal recommendation.

## Registry / supply-chain import
This lane is less about choosing a long-lived stack and more about keeping one-file work honest.

Imported public signals:
- crates.io development update:
  https://blog.rust-lang.org/2026/01/21/crates-io-development-update/
- RustSec advisories:
  https://rustsec.org/advisories/

Judgment:
- exact package identity still matters when a single-file script pulls dependencies;
- but this receipt does not claim that the one-file lane itself settles package-admission questions for those dependencies.

## API / compatibility import
Relevant current signals:
- Cargo unstable/reference surface:
  https://doc.rust-lang.org/cargo/reference/unstable.html
- Cargo changelog (`--publish-time`):
  https://doc.rust-lang.org/cargo/CHANGELOG.html

Imported facts:
- single-file packages are intentionally narrower than ordinary packages;
- lockfile and target-dir behavior differ from ordinary workspace expectations;
- replay/time-aware resolution features are becoming more interesting, but the lane is still primarily a communication/utility lane.

Compatibility judgment:
- the current caveat remains the correct public answer;
- the lane should not silently absorb stable-only or long-tail-support expectations.

## Maintenance / support-envelope import
Support-envelope facts that still hold:
- one-file shareability is the product value here;
- as soon as the artifact wants tests, structure, team ownership, or stable-only expectations, `cargo new` should win.

Maintenance judgment:
- the lane remains useful exactly because it is narrow;
- future revisions should resist the temptation to let “convenient for repros” become “good long-term maintenance strategy”.

## Freshness / replay notes
Fresh inputs checked on 2026-03-22:
- cargo-script goal:
  https://rust-lang.github.io/rust-project-goals/2024h2/cargo-script.html
- 2025H2 goals:
  https://blog.rust-lang.org/2025/10/28/project-goals-2025h2/
- 2026 flagships:
  https://rust-lang.github.io/rust-project-goals/2026/flagships.html
- program-management update:
  https://blog.rust-lang.org/inside-rust/2026/02/11/program-management-update-2026-01/
- Cargo unstable reference:
  https://doc.rust-lang.org/cargo/reference/unstable.html

Replay notes:
- renew this receipt whenever the stabilization status of single-file packages materially changes;
- the likely future change is not a lane replacement but a stronger or weaker caveat level.

## Lane judgment
Keep the card as **default-with-caveats**.

Why:
- it is the best current public answer for this narrow project class;
- the official Cargo momentum is too real to ignore;
- and the instability/support boundary is still too real to hide.

## Open watch items
- whether stabilization arrives soon enough to promote this from `default-with-caveats` to a normal default;
- whether future Cargo work changes the lockfile/discovery/support model enough to split the lane;
- whether the archive should eventually add a separate card for “tiny durable internal tool” that explicitly prefers `cargo new`.
