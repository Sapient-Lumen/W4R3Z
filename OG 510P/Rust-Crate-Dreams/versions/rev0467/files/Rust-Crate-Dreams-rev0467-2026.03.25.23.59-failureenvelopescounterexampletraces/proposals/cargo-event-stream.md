---
id: P-0042
title: cargo-event-stream — stable structured event handoff for Cargo sessions, foreign output, and portable build-stream bundles
status: idea
domains: [cargo, tooling, ide, observability]
last_reviewed: 2026-03-22
evidence:
  - https://blog.rust-lang.org/inside-rust/2026/01/07/this-development-cycle-in-cargo-1.93/
  - https://rust-lang.github.io/rust-project-goals/2025h2/cargo-build-analysis.html
  - https://blog.rust-lang.org/2026/03/13/call-for-testing-build-dir-layout-v2/
  - https://doc.rust-lang.org/cargo/reference/external-tools.html
  - https://doc.rust-lang.org/cargo/commands/cargo-doc.html
  - https://doc.rust-lang.org/cargo/commands/cargo-rustc.html
  - https://doc.rust-lang.org/beta/rustc/json.html
---
# Problem

The Rust/Cargo ecosystem now has more real build-observability substrate than it did when this proposal was first written.

- Cargo’s January 2026 development notes explicitly call out **structured logging** work.
- The Cargo build-analysis goal says Cargo wants to record build metadata across invocations and expose `cargo report` commands.
- Cargo’s external-tools docs still warn that `--message-format=json` only controls Cargo and rustc output and does **not** control arbitrary output from procedural macros or other tools.
- Cargo’s command docs now make rendering-policy choices like `json-render-diagnostics` explicit.
- The build-dir-layout-v2 testing call says many tools still rely on unspecified Cargo details because first-class features are missing.

That combination changes the shape of the missing crate.

The worthy contribution is no longer “invent a better private JSON mode for Cargo”.
It is a **stable event handoff layer** that helps tools and reviewers answer:

- which events are native Cargo/rustc events,
- which lines are foreign output that polluted the stream,
- what rendering policy shaped the diagnostics,
- which build session and command lane produced the stream,
- what redacted portable bundle is safe to hand off.

# What it provides

Core artifacts:

- `event-stream-profile.toml` — capture policy, raw-line policy, redaction policy, rendering expectations, and export rules.
- `cargo-event-envelope.ndjson` — stable top-level event envelope with session id, sequence, provenance, and event kind.
- `foreign-output.record.json` — explicit capture of proc-macro, build-script, runner, or other non-native output.
- `rendering-policy.receipt.json` — whether diagnostics were embedded, ANSI-rendered, Cargo-rendered, or mixed.
- `event-stream-session.manifest.json` — command lane, workspace root, profile, target posture, toolchain basis, and source inputs.
- `redaction.receipt.json` — what path/env/value classes were masked, preserved, or dropped.
- `event-stream-bundle.manifest.json` — portable bundle joining the stream, receipts, raw fragments, and notes.
- optional `notes.md` — compact explanation for CI uploads, issue reports, or IDE debugging.

CLI surface:

- `cargo event-stream capture -- <cargo args>`
- `cargo event-stream inspect`
- `cargo event-stream doctor`
- `cargo event-stream redact`
- `cargo event-stream bundle`
- `cargo event-stream diff old-bundle new-bundle`

# What the crate should provide other people

1. **One stable event envelope** for build-session tooling.
2. **One honest foreign-output story** instead of “just parse lines that start with `{`”.
3. **One rendering-policy receipt** instead of guessing whether `rendered` was embedded or Cargo-rendered.
4. **One session manifest** instead of vague “this came from a local build”.
5. **One redaction receipt** instead of silent truncation or path stripping.
6. **One portable bundle** that a maintainer, CI bot, or IDE plugin can inspect later.
7. **One library crate** for tools that should not each reinvent dirty-stream handling.

# Persona / who it’s for

- IDE and editor authors
- CI / build platform maintainers
- crate authors building developer tooling
- support engineers who need a portable build-session bundle

# Users & user stories

- **IDE author**: “Give me one session stream where native Cargo events, rustc diagnostics, and foreign output are clearly separated.”
- **CI maintainer**: “Attach one redacted bundle to a failed build without guessing which lines were JSON and which lines were proc-macro noise.”
- **Tool author**: “I want a small Rust crate that can parse and re-emit build-session events without scraping ad-hoc text.”
- **Reviewer**: “Tell me how diagnostics were rendered and what raw material got redacted before export.”

# Prior art (and why it’s insufficient)

- Cargo external-tools JSON is useful, but the docs explicitly warn that arbitrary tool and proc-macro output can still contaminate the stream.
- rustc JSON diagnostics are documented, but they are only one part of the build-session story.
- Cargo build-analysis is promising, but it is intentionally unstable and is aimed more at historical analysis and `cargo report` than at a stable event-handoff crate.
- `cargo_metadata::Message` parsing is useful, but it does not by itself solve foreign-output containment, rendering-policy receipts, or portable export.
- Raw stdout/stderr logs are not a reviewable contract.

# Design goals

- **Provenance-first** — every event says where it came from and what session it belongs to.
- **Foreign-output containment** — non-native output becomes explicit structured records, not silent parse failures.
- **Rendering-policy honesty** — embedded vs Cargo-rendered vs ANSI behavior is preserved.
- **Streaming-first** — NDJSON-style consumption remains cheap and incremental.
- **Bundle-first** — artifact handoff should become useful before any UI does.
- **Future-compatible** — import future Cargo structured-logging/build-analysis substrate without claiming ownership of Cargo’s recorder.
- **Conservative by default** — unknown or mixed lines become explicit records, not guesses.

# MVP surface

Minimal types:
- `EventStreamProfile`
- `CargoEventEnvelope`
- `ForeignOutputRecord`
- `RenderingPolicyReceipt`
- `EventStreamSessionManifest`
- `RedactionReceipt`
- `EventStreamBundleManifest`

Minimal functions:
- `capture_session_stream()`
- `normalize_event_line()`
- `capture_foreign_output()`
- `capture_rendering_policy()`
- `build_session_manifest()`
- `apply_redaction_policy()`
- `write_bundle()`

Feature flags:
- `serde`
- `capture`
- `redact`
- `bundle`
- `cargo-metadata-import`

# Compatibility story

- Starts by importing existing Cargo/rustc message streams instead of replacing them.
- Preserves unknown message kinds and raw lines explicitly.
- Leaves historical cross-run warehousing to **P-0035**.
- Leaves support-grade rebuild causality to **P-0469**.
- Leaves whole-run replay containers to **P-0057**.

# Conformance & fixtures

The fixture pack should freeze at least these scenarios:

- proc-macro stdout captured as foreign output rather than bare text;
- `json-render-diagnostics` preserved as rendering-policy truth;
- build-script metadata and compiler artifacts joined under one session identity;
- portable bundle that keeps native events, foreign output, and redaction truth separate.

# Path to boring stability

- Stabilize the event envelope, foreign-output record, rendering-policy receipt, session manifest, and bundle manifest before adding analytics.
- Start with capture/normalize/redact/export, not dashboarding.
- Treat raw preservation as a feature, not a failure.
- Import future upstream structured logging conservatively with provenance tags.

# Scorecard

- Impact: 5/5
- Neglectedness: 4/5
- Feasibility: 4/5
- Adoptability: 4/5
- Sustainability: 4/5
- Differentiation: 4/5
- **Total: 25/30**

# Minimum lovable MVP

A cargo subcommand and library that capture one build session, separate native Cargo/rustc events from foreign output, record rendering policy and session provenance, apply redaction policy, and emit one portable bundle.

# De-risk plan

1. Start with event envelopes and receipts rather than trying to replace Cargo internals.
2. Preserve raw lines and unknown message kinds explicitly.
3. Keep rendering policy first-class from day one.
4. Add richer import adapters only after the neutral bundle contract proves useful.

# Non-goals

- Not a replacement for Cargo’s future structured logging recorder.
- Not a historical trend warehouse.
- Not a rebuild-causality engine.
- Not a generic dashboard product.
- Not a promise that every line of build output can be normalized without loss.

# Architecture & API sketch

```rust
pub fn capture_session_stream(cx: &CaptureContext) -> Result<EventStreamCapture>;
pub fn normalize_event_line(
    profile: &EventStreamProfile,
    line: &str,
) -> Result<CargoEventEnvelope>;
pub fn capture_foreign_output(
    profile: &EventStreamProfile,
    line: &str,
) -> Result<ForeignOutputRecord>;
pub fn capture_rendering_policy(cx: &CaptureContext) -> Result<RenderingPolicyReceipt>;
pub fn build_session_manifest(cx: &CaptureContext) -> Result<EventStreamSessionManifest>;
pub fn apply_redaction_policy(bundle: &mut EventStreamBundle) -> Result<RedactionReceipt>;
pub fn write_bundle(bundle: &EventStreamBundle, out: &Path) -> Result<()>;
```

# Sources

- Cargo 1.93 development cycle — https://blog.rust-lang.org/inside-rust/2026/01/07/this-development-cycle-in-cargo-1.93/
- Prototype Cargo build analysis — https://rust-lang.github.io/rust-project-goals/2025h2/cargo-build-analysis.html
- Call for Testing: Build Dir Layout v2 — https://blog.rust-lang.org/2026/03/13/call-for-testing-build-dir-layout-v2/
- Cargo external-tools JSON docs — https://doc.rust-lang.org/cargo/reference/external-tools.html
- Cargo message-format docs — https://doc.rust-lang.org/cargo/commands/cargo-doc.html
- Cargo build/rustc docs — https://doc.rust-lang.org/cargo/commands/cargo-rustc.html
- rustc JSON output docs — https://doc.rust-lang.org/beta/rustc/json.html
