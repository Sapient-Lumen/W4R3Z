---
id: P-0046
title: buildscript-ux-kit — structured build-script diagnostics, summaries, and policy hooks
status: idea
domains: [cargo, tooling, dx, build-scripts]
last_reviewed: 2026-03-08
evidence:
  - https://doc.rust-lang.org/cargo/reference/build-scripts.html
  - https://doc.rust-lang.org/cargo/reference/external-tools.html
  - https://doc.rust-lang.org/cargo/reference/unstable.html
  - https://github.com/rust-lang/cargo/issues/10159
  - https://github.com/rust-lang/cargo/issues/15038
  - https://github.com/rust-lang/cargo/issues/15792
---

# Problem
Build scripts (`build.rs`) are powerful and common, but their **user experience is repeatedly reported as noisy and confusing**:

- When a build script fails, Cargo often dumps large stdout/stderr logs where the actual “fix this package” message is hard to find.
- `cargo::warning` is intentionally **not shown by default** for non-path dependencies unless the build fails or the user opts into `-vv`, which means real compatibility or support warnings can stay invisible in common downstream installs.
- `cargo::error` is real and useful, but current Cargo behavior still leaves awkward cases where the concise structured error is followed by a large dump if the script exits non-zero.
- Cargo’s JSON stream already includes `build-script-executed` messages, but those messages only cover parsed outputs such as link/search/cfg/env/out_dir; they are not yet a human-scale support artifact.
- Cargo may emit cached build-script results even when the script did not run, so a serious support bundle must distinguish **observed-live** from **imported-cached** truth.

This causes real friction for end users (“Rust won’t compile and I can’t see why”), for maintainers (“my build script tried to tell the user exactly what to install”), and for tool authors (“I still need a stable bundle, not just raw mixed logs and partial JSON”).

# Users & user stories
- **End users**: “Tell me the one line that fixes my build (`apt install ...`, set an env var, enable a feature, or use the vendored path).”
- **CI maintainers**: “I want to gate on build-script warnings for *my* workspace, but not fail on every noisy transitive crate by default.”
- **Library authors**: “I want to emit multi-line, well-formatted diagnostics from build.rs without them being buried under rerun directives and tool chatter.”
- **Tool / IDE authors**: “I want structured build-script diagnostics with package identity, visibility, and capture-origin semantics.”

# Prior art (and why it’s insufficient)
- Cargo has directives like `cargo::warning` and `cargo::error`, but the end-user presentation is still frequently noisy in practice, and visibility rules mean warnings from registry dependencies can be hidden by default. (Evidence links.)
- Cargo already emits machine-readable `build-script-executed` messages under `--message-format=json`, but that surface intentionally covers parsed results, not a full downstream support bundle. (Evidence links.)
- Cargo has unstable `metabuild` and `multiple-build-scripts`, which shows upstream interest in more declarative / unit-based build behavior. That means a serious crate should not hard-code “one handwritten `build.rs` file forever” into its model. (Evidence link.)
- Multiple long-lived Cargo issues still report that build-script failures remain hard to read even after earlier improvements. (Evidence links.)

# Design goals
- Provide a **structured capture and summarization layer** for build-script output and directives:
  - parse `cargo::warning`, `cargo::error`, `cargo::rerun-if-changed`, `cargo::rustc-link-*`, `cargo::metadata`, and friends,
  - capture stdout/stderr with strong defaults (truncate, keep last N lines, highlight directives),
  - import Cargo JSON when available and mark whether the report came from a live run or cached `build-script-executed` messages,
  - emit machine-readable summaries (JSON/NDJSON) and a concise human report.
- Provide **policy hooks**:
  - “fail on build-script warnings for workspace members” (opt-in),
  - flag warnings that would normally be hidden for non-path dependencies,
  - ignore/suppress known-noisy transitive warnings unless the build actually failed,
  - allow pluggable allow/deny rules per crate or warning class.
- Be able to integrate with, or eventually be subsumed by, future Cargo improvements; do not fight upstream.

# Non-goals
- Replacing build scripts with a new build system.
- Solving every FFI or native toolchain issue; the goal is **presentation + policy + support artifacts**, not fixing C compilers.
- Pretending Cargo already exposes a perfect causal model.
- Forcing new syntax on Cargo; a first version can start as a wrapper / external-tooling layer.

# Architecture & API sketch
## Core model
- `BuildscriptObservation`
  - one build-script execution/import unit
  - package identity, optional script name, capture origin, cached/live marker
- `BuildscriptReport`
  - observed directives (typed)
  - messages with visibility and redaction metadata
  - suggested fix candidates
  - stdout/stderr excerpts + full-log pointers
  - workspace policy results
- `BuildscriptPolicy`
  - deny/allow rules for warnings, hidden-warning escalation, crate selectors

## Import paths
- `BuildscriptImport::from_cargo_json(reader)`
  - import `build-script-executed` plus package identity and freshness/cached signals when available
- `BuildscriptImport::from_raw_streams(stdout, stderr, cfg)`
  - parse directives and preserve excerpts when raw logs are all that exist
- `BuildscriptImport::merge(json, raw)`
  - prefer Cargo’s parsed data where possible and treat raw log parsing as a supplement, not the source of truth

## CLI (initial delivery)
- `cargo buildscript report [--] <cargo args...>`
  - runs Cargo, captures relevant output, emits `target/buildscript-report.json` + terminal summary
- `cargo buildscript summarize path/to/buildscript-report.json`
  - renders a concise human summary from an existing bundle
- `cargo buildscript gate --deny-warnings`
  - workspace-scoped policy gate by default

## Integrations
- Optional integration with `cargo-event-stream` (P-0042): build-script events become first-class events in the overall build stream.
- Optional later integration with `P-0059 buildscript-testkit`: fixture outputs normalize to the same report vocabulary.

# Security / safety model
- Logs may contain secrets (env vars, tokens, absolute paths). Default to:
  - redaction patterns,
  - path placeholders,
  - truncation,
  - opt-in full-log preservation.
- Clearly mark provenance: which crate / unit emitted which message, and whether the report reflects a live execution or cached Cargo state.

# Maintenance & governance
- Keep dependencies small; prefer pure Rust parsing and lightweight Cargo JSON import.
- Maintain a shared fixture suite of common failure/support cases:
  - `pkg-config` failure,
  - hidden transitive warning,
  - `cargo::error` plus non-zero exit,
  - rerun-noise overload,
  - cached build-script result import,
  - redaction-sensitive output.
- Document “best practices for build.rs diagnostics” and provide helper notes for maintainers.

# Success criteria
- Users can reliably see and act on the *actual* build failure reason.
- CI can gate on workspace build-script warnings without becoming unusable.
- IDEs/tools can render build-script diagnostics without scraping free-form text only.
- Reports clearly distinguish “script ran now” from “Cargo surfaced cached build-script results”.


## What this crate should provide other people

This crate should give other people one boring answer to:

> “What happened in `build.rs`, what was hidden by default, and what should I do next?”

Other people should get:

- `buildscript-report.json` — normalized directives, messages, visibility, capture origin, stdout/stderr excerpts, and redaction metadata.
- `buildscript-summary.txt` — one screen of human-first output that highlights the likely fix rather than dumping every `rerun-if-*` line.
- `policy-gate.report.json` — whether workspace policy was violated (`deny_warnings`, hidden-warning escalation, forbidden env usage, noisy transitive script, etc.).
- `notes.md` — optional maintainer-authored help text for known failure classes.

That makes the crate useful to:

- end users trying to install or build a crate,
- CI maintainers who want reviewable policy failures,
- IDE authors who want structured build-script diagnostics,
- and maintainers who want a support artifact instead of “please rerun with `-vv` and paste 200 lines.”

## 0.1 boundaries

A good 0.1 should:

- import Cargo JSON when available and supplement it with raw stdout/stderr excerpts,
- capture directives and summarize them without pretending Cargo exposes perfect causality,
- surface warnings that would normally be hidden for non-path dependencies,
- highlight the shortest actionable failure message,
- keep full-log retention opt-in and redacted by default,
- and scope policy gates to workspace members first.

A bad 0.1 would try to replace Cargo itself, redesign the build-script protocol, or solve every native toolchain failure.

## Recommended 0.1 crate split

Keep the first release intentionally small:

- `buildscript-report-core` — parse/normalize directives, messages, visibility, capture origin, and redaction state
- `cargo-buildscript-report` — CLI or cargo-subcommand surface for report / gate / summarize
- optional later helper crate for maintainer-side nicer diagnostic emission

This keeps the value centered on **support artifacts**, not on replacing Cargo.

## Upstream fit

This crate should prefer Cargo’s existing `--message-format=json` surfaces and package/build-unit identity when they are available, and only treat raw stdout/stderr capture as a supplement.

The value is not to redesign the build-script protocol. The value is to add **summaries, visibility semantics, policy gates, redaction, and support artifacts** above the protocol Cargo already exposes.

It should also stay compatible with Cargo’s more declarative direction (`metabuild`, `multiple-build-scripts`) by modeling **build-script units / observations**, not assuming one permanent file-path-shaped script identity.
