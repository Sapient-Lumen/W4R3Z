# Default card: Script / repro / tiny utility (2026 Q1)

Latest renewal receipt: `evidence/script-repro-tiny-utility-2026Q1-renewal-2026-03-22.md`


## Scope
This card applies to:
- single-purpose scripts and throwaway utilities;
- reproducible bug reports and shared examples;
- quick prototypes where one file is a feature, not a compromise;
- teaching material and snippets that benefit from embedded dependencies.

Assumptions:
- the artifact is small and intentionally bounded;
- a single-file package is a good fit for the communication surface;
- the code is not yet a long-lived workspace member;
- nightly Cargo features are acceptable when the scope truly matches this lane.

This is **not** the default for:
- durable internal tooling that will obviously grow;
- crates meant for publication and long maintenance tails;
- multi-binary or multi-library layouts;
- or team environments that require stable-only workflows.

## Why this default now
Rust has been explicit that single-file packages are a strategic quality-of-life improvement, not a side experiment.
The cargo-script goal says single-file packages reduce friction for bug reports, educational material, prototyping, and small utilities.
https://rust-lang.github.io/rust-project-goals/2024h2/cargo-script.html

The current Cargo reference for unstable features shows that single-file packages with embedded manifests already exist on nightly, with explicit constraints around manifest fields, lockfile location, and non-discovery.
https://doc.rust-lang.org/cargo/reference/unstable.html

The January 2026 program-management update describes cargo-script as one of the most anticipated features and emphasizes that having a single file you can share or paste into Markdown makes a practical difference for repros and prototypes.
https://blog.rust-lang.org/inside-rust/2026/02/11/program-management-update-2026-01/

For this exact project class, the archive’s current answer is:
**use cargo-script / single-file packages as the default-with-caveats lane, and escalate to an ordinary Cargo package as soon as the artifact stops being genuinely single-file in spirit.**

## Decision label
**default-with-caveats**

It is the best current reusable starting lane for this exact scope, but it is still on the stabilization path and should not be over-read as the answer for normal long-lived projects.

## Default lane summary
### Default lane
- subject form: **single `.rs` file**
- packaging model: **embedded manifest (frontmatter)** when dependencies/settings are needed
- launch model: **cargo script / single-file package invocation**
- dependency posture: **small, explicit, communication-first**
- upgrade path: **promote to a normal Cargo package when growth starts**

### Serious alternative
- **ordinary Cargo package (`cargo new`)** when stability, team ergonomics, testing structure, or expected growth matter more than one-file shareability.

### Watch / not-default here
- large one-file scripts accumulating more responsibilities;
- org-local wrappers that hide Cargo behavior;
- unstable single-file workflows used as if they were already the universal project default.

## Slot guidance
### Subject slot
Prefer a single-file package only when the file itself is part of the product value:
- easy to share,
- easy to paste into docs/issues,
- easy to run as a small utility.

If the project’s real shape is already multi-file, skip this lane.

### Manifest slot
Prefer embedded manifest frontmatter only for the small set of dependencies and settings that improve the one-file workflow.
The Cargo reference explicitly disallows several manifest fields and makes clear that single-file packages are intentionally narrower than ordinary packages.
https://doc.rust-lang.org/cargo/reference/unstable.html

### Target / state slot
Be honest that Cargo uses a target dir under `$CARGO_HOME/target/<hash>` for single-file packages and places the lockfile in that target dir.
That helps avoid directory clutter and read-only-parent problems, but it also means this is not the same operational model as a regular workspace.
https://doc.rust-lang.org/cargo/reference/unstable.html

### Growth slot
The default growth path is not “keep stretching the script forever”.
The default growth path is:
**promote to a normal Cargo package once the code wants structure, tests, reuse, or team ownership.**

## Serious alternatives and when they win
### Ordinary Cargo package wins when
- stable-only workflows are required;
- the utility will be kept for a long time;
- testing, module structure, or CI integration is already expected;
- multiple binaries, examples, or supporting files are emerging;
- or the script is becoming a real internal tool rather than a communication artifact.

## Escalate to a project-specific brief when
- the script is going to be distributed or supported as a product;
- it needs more than a very small dependency/config surface;
- local policy requires SBOM, package-admission, or stronger lifecycle evidence;
- the artifact must integrate deeply with an existing workspace;
- or the team is using the single-file form to avoid making an actual project decision.

## Canonical references
- cargo-script goal:
  https://rust-lang.github.io/rust-project-goals/2024h2/cargo-script.html
- 2026 flagships / higher-level Rust:
  https://rust-lang.github.io/rust-project-goals/2026/flagships.html
- program-management update with concrete examples:
  https://blog.rust-lang.org/inside-rust/2026/02/11/program-management-update-2026-01/
- Cargo unstable feature reference for `script` / single-file packages:
  https://doc.rust-lang.org/cargo/reference/unstable.html

## Imported evidence and renewal inputs
Recheck before renewal:
- stabilization progress for cargo-script;
- current Cargo reference behavior around embedded manifests, discovery, and lockfiles;
- whether the workflow is still explicitly recommended for bug repros, examples, and tiny utilities;
- whether the card should remain `default-with-caveats` or become a stable default.

Signal refs:
- https://rust-lang.github.io/rust-project-goals/2024h2/cargo-script.html
- https://rust-lang.github.io/rust-project-goals/2026/flagships.html
- https://blog.rust-lang.org/inside-rust/2026/02/11/program-management-update-2026-01/
- https://doc.rust-lang.org/cargo/reference/unstable.html

## Non-goals
- declaring single-file packages the answer for ordinary long-lived Rust applications;
- hiding that the workflow is still partly unstable as of 2026 Q1;
- replacing normal Cargo packages for shared team-owned tools;
- or letting a convenient repro/prototype path silently become a maintenance strategy.
