# Cargo event-stream product plan — 2026-03-22

This note sharpens **P-0042 cargo-event-stream** into a buildable product plan.

## Why this lane is worthy now

Fresh Cargo and Rust sources align unusually well:

- Cargo’s active structured-logging work means build-event substrate is no longer hypothetical;
- the build-analysis goal says Cargo wants recorded build metadata and explicit `cargo report` surfaces;
- Cargo’s own docs still warn that `--message-format=json` cannot tame arbitrary proc-macro or tool output;
- message-format policy keeps growing more nuanced (`json-diagnostic-short`, `json-diagnostic-rendered-ansi`, `json-render-diagnostics`), which means event consumers need rendering truth, not only message blobs.

The sharper missing value is therefore not “more JSON from Cargo.”
It is a crate that helps another engineer inspect **what events are native**, **what output is foreign noise but still important**, **what rendering policy was active**, **what session produced the stream**, and **what redacted bundle remains safe to share**.

## Product thesis

The crate should become the boring support layer above:

- Cargo `--message-format=json`,
- rustc JSON diagnostics,
- future Cargo structured logging,
- build-analysis session ids and report commands,
- build-script / proc-macro / runner output that currently pollutes the stream.

Its job is to freeze those moving parts into a compact set of reviewable receipts.

## MVP artifact order

1. `event-stream-profile.toml`
2. `cargo-event-envelope.ndjson`
3. `foreign-output.record.json`
4. `rendering-policy.receipt.json`
5. `event-stream-session.manifest.json`
6. `redaction.receipt.json`
7. `event-stream-bundle.manifest.json`
8. `notes.md`

## First useful scenarios

1. Proc-macro stdout is captured as explicit foreign output rather than silently breaking the stream.
2. `json-render-diagnostics` is preserved as rendering policy rather than lost in the capture layer.
3. Build-script metadata and compiler-artifact messages share one session identity and sequence story.
4. Portable export keeps native events, foreign output, and redaction truth separate.

## Receiver-facing promise

A good bundle from this lane should let another engineer answer five questions fast:

1. What command/session produced this stream?
2. Which events came from Cargo/rustc and which lines were foreign output?
3. What rendering policy shaped the diagnostics?
4. Was anything dropped, repaired, or only captured as raw text?
5. What redacted export is safe to hand to CI, IDEs, or another human?

## What the crate should provide other people

1. **One stable event envelope** instead of bespoke parsers around unstable line noise.
2. **One foreign-output containment story** instead of line-prefix heuristics spread across tools.
3. **One rendering-policy receipt** so ANSI/rendered/Cargo-rendered differences stay reviewable.
4. **One session manifest** that names command lane, profile, workspace root, target posture, and toolchain basis.
5. **One redaction receipt** describing what path/env/material policy touched the export.
6. **One portable bundle** that downstream bots or maintainers can inspect without rerunning the build.
7. **One library/CLI pair** for IDE, CI, and support-tool authors who should not each reinvent dirty-stream handling.

## Things this product should resist

- becoming Cargo’s canonical internal recorder;
- becoming the historical build warehouse owned more cleanly by **P-0035**;
- becoming the support-grade rebuild-cause bundle owned by **P-0469**;
- becoming a general replay container owned more naturally by **P-0057**;
- pretending all non-JSON output is meaningless and can be discarded.
