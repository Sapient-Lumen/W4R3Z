---
id: P-0242
title: Reproducible Build Evidence Kit — Rust-first build recipes, rebuild verdicts, and diff triage bundles
status: idea
domains: [supply-chain, build-systems, reproducibility, security, cargo]
last_reviewed: 2026-03-09
evidence:
  - https://reproducible-builds.org/docs/rust/
  - https://reproducible-builds.org/docs/recording/
  - https://reproducible-builds.org/specs/source-date-epoch/
  - https://diffoscope.org/
  - https://doc.rust-lang.org/cargo/reference/unstable.html#profile-trim-paths-option
  - https://doc.rust-lang.org/beta/unstable-book/compiler-flags/remap-cwd-prefix.html
  - https://github.com/google/oss-rebuild
  - https://security.googleblog.com/2025/07/introducing-oss-rebuild-open-source.html
---

# P-0242 — Reproducible Build Evidence Kit

**Codename:** `reprobuild`

**Primary surface:** a crate workspace plus `cargo reprobuild` / `cargo repro`.

**Canonical artifact:** `*.reprobuildbundle.zip`, ideally as a `reprobuildbundle@1` profile on top of **P-0256 Evidence Bundle Core Kit**.

## Problem

Rust often gets surprisingly close to reproducible builds already, but the last mile is still too manual and too folklore-heavy.

Today, if a maintainer or downstream rebuilder wants to answer:

> “Did this crate rebuild cleanly, and if not, what exactly drifted?”

…they usually have to stitch together:

- ad hoc shell scripts,
- copies of `Cargo.lock`,
- environment notes in CI logs,
- a `diffoscope` invocation,
- and a human interpretation of whether the result is suspicious, harmless, or just a normalization gap.

That is not a good ecosystem default.

The missing crate is not just “a Rust wrapper around diffoscope”.
It is a **reproducibility evidence kit** that freezes four receiver-facing artifacts:

1. a **build recipe**,
2. a **rebuild verdict**,
3. a **diff triage report**,
4. and one portable **bundle** that carries them together.

## Main judgment

A worthy crate contribution here would give other people one honest answer to:

> “What source/toolchain/environment was claimed, what did the rebuilder actually do, did the artifacts match bit-for-bit or semantically, and what is the smallest useful explanation for any drift?”

That answer should be compact, reviewable, and explicit about uncertainty.

## What the crate should provide other people

### 1. A build recipe artifact
The crate should emit a small, diffable **recipe** rather than dumping raw CI state.

That recipe should record things like:

- package name/version,
- source identity (git revision or registry tarball digest),
- `Cargo.lock` digest,
- target triple,
- `rustc` / `cargo` versions,
- linker lane,
- selected features/profile,
- `--locked` / offline expectations,
- and the relevant reproducibility knobs (`SOURCE_DATE_EPOCH`, path remapping, trim-paths, locale/TZ policy).

This is the Rust-shaped equivalent of a `.buildinfo`-style “how to replay this build” description.

### 2. A rebuild verdict artifact
The crate should not force every mismatch into one scary bucket.

A useful verdict surface should distinguish at least:

- `reproduced` — bit-for-bit match,
- `semantically-reproduced` — normalized comparison says the important content matches,
- `mismatch` — material differences remain,
- `not-comparable` — the result set does not support a fair comparison,
- `manual-review-required` — the tool cannot honestly classify the result.

That distinction matters because reproducibility work increasingly lives in a world of normalization and artifact interpretation, not only byte equality.

### 3. A diff triage report
The crate should summarize *why* things differ, not just attach an unreadable blob.

The report should classify top causes such as:

- timestamp drift,
- path-prefix leakage,
- archive-entry ordering,
- compression-only variance,
- build-id / linker metadata,
- generated-code or build-script drift,
- or unknown / mixed causes.

A good triage report should point another person toward the next action, not merely prove that bytes changed.

### 4. A portable bundle
The output should be `*.reprobuildbundle.zip` and should carry:

- official and/or rebuilder recipes,
- verdict report,
- diff summary,
- optional raw diffoscope outputs,
- optional normalized artifact projections,
- and minimal replay instructions.

The bundle should reuse **P-0256** for deterministic packing, redaction, signatures, and diffing rather than reinventing that substrate.

### 5. An honest CLI workflow
The crate should provide a boring default path:

- `cargo reprobuild capture`
- `cargo reprobuild compare`
- `cargo reprobuild explain`
- `cargo reprobuild bundle`
- `cargo reprobuild diff`

The first release does not need to own every rebuild environment. It does need to give maintainers a clean, reviewable workflow.

## Persona / who it’s for

- crate maintainers who want a credible reproducibility story
- downstream packagers and distro integrators
- supply-chain/security engineers reviewing third-party artifacts
- CI/release engineers who need something more portable than logs
- ecosystem rebuild services that want a Rust-native receiver surface

## Users & user stories

- **Maintainer:** “Tell me whether my crate rebuilt cleanly on another machine, and if not, whether the drift is probably timestamps, paths, compression, or something more serious.”
- **Downstream rebuilder:** “Give me one bundle I can attach to an issue instead of pasting shell commands and screenshots.”
- **Security reviewer:** “Separate exact reproduction from semantic reproduction and from unresolved mismatch.”
- **Registry-scale rebuilder:** “Export one stable result contract for Rust packages instead of inventing yet another private attestation payload.”

## Prior art scan (and why it’s insufficient)

### Reproducible Builds substrate
The Reproducible Builds ecosystem already documents several key pieces:

- Rust-specific advice around `Cargo.lock`, diffing `target/`, `SOURCE_DATE_EPOCH`, and common failure modes,
- `.buildinfo` / build-environment recording conventions,
- and the broader notion that build metadata should travel as a separate reviewable artifact.

That is strong substrate, but it does not by itself give Rust teams one compact, Cargo-native receiver artifact.

### diffoscope
`diffoscope` is the right baseline comparison engine because it already knows how to recursively unpack many archive and binary formats.
But `diffoscope` output is not itself the missing product.
The missing product is the **Rust-shaped triage and receipt layer above it**.

### Cargo/rustc path hygiene
Cargo and rustc now expose more path-sanitization substrate than before:

- `trim-paths` exists as a Cargo profile option,
- and `-Z remap-cwd-prefix` exists to rewrite absolute paths under the current working directory.

That is useful substrate, but it does not yet freeze the review artifact another person needs when a build still drifts.

### OSS Rebuild
OSS Rebuild is an important external signal that this area is timely, not hypothetical.
It rebuilds upstream packages, semantically compares results, and publishes attestations across ecosystems including crates.io.
That makes the Rust-native gap sharper: maintainers and tool authors still lack a small local crate/workflow that emits **rebuild recipes, verdicts, and triage bundles** in a way ordinary teams can reuse.

## Design goals

1. **Recipe-first** — capture the replayable build claim, not just the outcome.
2. **Verdict honesty** — bitwise match, semantic match, unresolved mismatch, and unsupported cases must stay distinct.
3. **Triage before theory** — point to likely causes and next actions.
4. **Bundle-first sharing** — another person should be able to inspect the evidence without reverse-engineering CI.
5. **Reuse substrate** — lean on `diffoscope`, Cargo/rustc reproducibility knobs, and P-0256 rather than cloning them.
6. **Conservative by default** — when the tool cannot safely classify a difference, it should say so.

## Proposed architecture

```text
reprobuild-core/         # recipe model, verdict model, diff triage model
reprobuild-cargo/        # cargo subcommands, workspace/package capture
reprobuild-compare/      # comparators, normalization rules, diffoscope adapter
reprobuild-bundle/       # reprobuildbundle profile over evidencekit
reprobuild-cli/          # cargo reprobuild
```

## Core artifacts

### `build-recipe.json`
A compact record of:

- package identity,
- source identity,
- lockfile digest,
- toolchain,
- target/profile/features,
- relevant env/config knobs,
- artifact expectations,
- and declared normalization assumptions.

### `rebuild-verdict.json`
A normalized result stating:

- the compared subjects,
- comparison mode (bitwise and/or semantic),
- exact outcome classification,
- what normalizations were applied,
- confidence / caveats,
- and the digest of the recipe(s) it refers to.

### `diff-summary.json`
A machine-readable triage layer over raw comparator output:

- top cause classes,
- affected artifacts,
- likely next actions,
- severity / suspicion hints,
- and pointers to raw reports like HTML/JSON diffoscope outputs.

### `*.reprobuildbundle.zip`
A portable bundle carrying those artifacts together.

## Fixture-first MVP

The 0.1 release should **not** promise “universal reproducible Rust builds.”
It should promise one small review contract:

1. capture a build recipe,
2. compare two build outputs,
3. classify the result honestly,
4. emit a triage summary,
5. package the result into one bundle.

That is already enough to make the crate useful in CI, issue reports, release reviews, and registry-scale rebuilding experiments.

## Suggested 0.1 scenario set

1. **Compression-only drift** — byte mismatch, semantic match after normalization.
2. **Absolute-path leak** — path-prefix drift from missing remap/trim configuration.
3. **Timestamp drift** — `SOURCE_DATE_EPOCH` absent or inconsistently propagated.
4. **Build-script generated file drift** — recipe says sources match, but generated content differs.
5. **Not-comparable result** — subjects differ in target/profile/features, so the tool refuses a fake verdict.

## Scope boundaries / non-goals

- Not a replacement for `diffoscope`.
- Not a full hosted rebuild service.
- Not a guarantee that every Rust crate is reproducible.
- Not a substitute for provenance/attestation systems like SLSA.
- Not the generic evidence substrate itself; that belongs in **P-0256**.

## Adoption plan

1. Start with `cargo build --locked` / workspace-local capture.
2. Shell out to `diffoscope` first rather than cloning its comparators.
3. Make the bundle attachable in GitHub issues and CI artifacts.
4. Add adapters for hosted rebuild services and attestation systems later.
5. Encourage protocol/interop crates in this archive to import `reprobuildbundle` when they need build-evidence lanes.

## Why this looks more worthy now

This proposal is stronger than a generic “Rust reproducibility helper” because it now answers the handoff question clearly:

- **What does it hand another person?**
  A recipe, a verdict, a diff triage report, and one bundle.

- **What does it reuse instead of duplicating?**
  Reproducible Builds guidance, `diffoscope`, Cargo/rustc path hygiene, and evidence-bundle substrate.

- **Why now?**
  Because external work like OSS Rebuild shows the ecosystem is moving from “can we rebuild packages at all?” to “what stable result contract should downstream reviewers consume?”
