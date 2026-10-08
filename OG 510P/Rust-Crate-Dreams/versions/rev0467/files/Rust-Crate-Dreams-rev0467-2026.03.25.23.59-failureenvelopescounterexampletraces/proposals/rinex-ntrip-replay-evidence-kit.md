---
id: P-0379
title: RINEX 4.02 + NTRIP v2 Replay & Evidence Kit — stream/file parity, station-profile locks, and portable GNSS incident bundles
status: idea
domains: [gnss, geodesy, streaming, telemetry, science, interoperability, validation]
last_reviewed: 2026-03-06
evidence:
  - https://igs.org/formats-and-standards/
  - https://igs.org/wg/rinex/
  - https://www.rtcm.org/publications
  - https://github.com/nav-solutions/rinex
  - https://docs.rs/ntrip-client
  - https://docs.rs/crate/gnss-qc/0.4.0/source/README.md
---

# Problem

Rust now has real GNSS substrate: there is an active `rinex` parser/formatter, multiple NTRIP client crates, and GNSS quality-control work. But the operational pain still sits at the seam between:

- **real-time correction streams and archived exchange files**,
- **station/profile expectations and what the stream actually carries**,
- **header metadata and downstream processing assumptions**,
- **QC findings and the raw stream/file evidence needed to explain them**,
- and **“it works on this caster / station / toolchain” incidents that are hard to replay elsewhere**.

The missing Rust contribution is not another low-level parser. It is a **stream/file replay and evidence kit** that can connect NTRIP sessions, RINEX artifacts, and QC findings into one portable debugging surface.

# What it provides

- `gnss-profile.lock` — pins RINEX version/profile, station assumptions, observation/nav file expectations, stream metadata, and QC thresholds.
- `gnss-irx` — a neutral IR for station headers, observation summaries, stream/session metadata, timing gaps, and QC findings.
- `stream-capture` — captures and normalizes NTRIP session metadata and selected correction / timing evidence.
- `stream-file-diff` — compares NTRIP-derived evidence, projected file summaries, and actual RINEX files for drift or loss.
- `cargo gnss-evidence` — emits `*.gnssbundle.zip` with lockfile, session summary, header/profile diff, QC findings, and notes.

# What the crate should provide other people

1. **A boring default artifact for GNSS ingest/debug incidents**.
2. **Explicit station/profile locks** instead of vague “supports RINEX / NTRIP”.
3. **Replayable stream/file parity checks** for operators and library maintainers.
4. **Portable QC evidence** that ties findings back to session and file context.
5. **A shared bundle format** for handoff across data providers, integrators, and Rust tools.

# Persona / who it’s for

- GNSS / geodesy platform teams collecting or distributing data
- Rust maintainers building RINEX/NTRIP/quality-control tools
- Operators debugging station or caster behavior
- Researchers trying to reproduce ingest or metadata issues from shared evidence

# Users & user stories

- **Operator**: “Tell me whether the failure came from the stream, the projected file, or a downstream profile assumption.”
- **Maintainer**: “Run one fixture corpus across RINEX parsing, NTRIP capture, and QC layers.”
- **Research user**: “Share enough evidence to reproduce a station issue without shipping a giant raw dataset.”
- **Integrator**: “Diff what the station promised against what the header/stream actually contained.”

# Prior art (and why it’s insufficient)

- IGS now treats RINEX 4.02 as current and encourages modern RINEX use.
- RTCM publishes Ntrip v2 as the standard transport surface for RTCM-over-IP distribution.
- Rust already has the `rinex` project, NTRIP client crates, and GNSS quality-control work.

What Rust still lacks is a **boring default workbench** for profile locks, stream/file parity, normalized QC evidence, and portable incident bundles.

# Design goals

1. **Stream/file continuity** — treat real-time and archive surfaces as one debugging problem.
2. **Station-profile explicitness** — make assumptions reviewable.
3. **QC-linked evidence** — every finding should be traceable to compact evidence.
4. **Large-artifact discipline** — bundles must stay compact enough for Git/issue trackers.
5. **Adapter-first** — reuse existing parsers and QC tools.

# MVP surface

- Minimal types: `GnssProfileLock`, `StationSummary`, `QcFinding`, `GnssBundle`
- Minimal functions:
  - `inspect_rinex()`
  - `capture_ntrip_session()`
  - `diff_stream_vs_file()`
  - `write_bundle()`
- Feature flags:
  - `rinex4`
  - `ntrip`
  - `qc`
  - `sampling`
  - `redaction`

# Compatibility story

- Starts above existing Rust GNSS crates rather than replacing them.
- Can operate on summarized sessions or sampled excerpts when raw data is too large.
- Treats stream adapters, file parsers, and QC engines as pluggable inputs into one stable evidence schema.
- Keeps station/profile quirks explicit in overlays.

# Conformance & fixtures

- Tiny fixtures for header drift, timestamp gaps, profile/version mismatches, session auth/reconnect issues, and QC threshold disagreements.
- Goldens for “same station, different stream metadata” and “same stream, different file interpretation”.
- Public fixture packs using small observation/nav excerpts and synthetic session traces.
- Projected-file fixtures that compare summarized stream evidence against actual RINEX outputs.

# Path to boring stability

- Stabilize lockfile, report schema, and parity-diff categories before widening transport or message coverage.
- Start with session metadata, timing, header/profile, and QC-linked evidence rather than raw full-session capture.
- Keep the first scope on incidents and reproducibility, not a full RTK processing stack.
- Prefer deterministic sampling and summary generation.

# Scorecard

- Impact: 4/5
- Neglectedness: 4/5
- Feasibility: 3/5
- Adoptability: 4/5
- Sustainability: 4/5
- Differentiation: 4/5
- **Total: 23/30**

# Minimum lovable MVP

A library and CLI that inspect a small RINEX artifact, normalize one NTRIP session summary, run narrow parity/QC checks, and emit a `*.gnssbundle.zip` linking station profile, session evidence, and findings.

# De-risk plan

1. Start with metadata/timing/header parity rather than decoding every possible message surface.
2. Keep bundles compact with summaries and sampled excerpts.
3. Reuse existing Rust crates for parsing and QC.
4. Make profile/version assumptions explicit from day one.

# Non-goals

- Not a full RTK engine.
- Not a replacement for existing GNSS processing suites.
- Not a data-hosting service.
- Not a full standards implementation for all RTCM message families.

# Architecture & API sketch

```rust
pub struct GnssProfileLock {
    pub rinex_version: String,
    pub station_policy: String,
    pub qc_profile: String,
}

pub fn inspect_rinex(bytes: &[u8]) -> Result<RinexReport>;
pub fn diff_stream_vs_file(stream: &SessionReport, file: &RinexReport, lock: &GnssProfileLock) -> ParityDiff;
```

Bundle draft: `gnss-profile.lock`, `session-summary.json`, `rinex-summary.json`, `qc-findings.json`, `parity-diff.json`, `notes.md`.

# Security / safety model

- Treat session metadata and station details as potentially sensitive.
- Support redaction of credentials, endpoints, and precise site-identifying metadata where needed.
- Record exact parser/QC/adapter versions in every bundle.
- Keep outputs deterministic for CI and collaborative debugging.

# Maintenance & governance plan

- Keep the core centered on profile locks, neutral summaries, parity findings, and bundle format.
- Version adapters independently where necessary.
- Publish a small public corpus of safe station/session fixtures.
- Avoid turning the project into an all-in-one geodesy framework.

# Milestones

## 0.1
- RINEX inspection
- NTRIP session summary ingestion
- profile lockfile

## 0.2
- parity diffing
- QC adapters
- redaction and sampling

## 1.0
- stable `*.gnssbundle.zip`
- public fixture corpus
- documented compatibility policy across supported stream/file surfaces

# Open questions

- How much RTCM/session detail belongs in MVP before bundles become too large or adapter-specific?
- Which QC outputs are worth normalizing first?
- What is the smallest projected-file model that still explains stream/file drift?

# Sources

- IGS formats and standards: https://igs.org/formats-and-standards/
- IGS RINEX working-group page: https://igs.org/wg/rinex/
- RTCM publications page (Ntrip v2): https://www.rtcm.org/publications
- `rinex` Rust project: https://github.com/nav-solutions/rinex
- `ntrip-client`: https://docs.rs/ntrip-client
- `gnss-qc`: https://docs.rs/crate/gnss-qc/0.4.0/source/README.md
