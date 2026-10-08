---
id: P-0297
title: FIX + FIXT + Orchestra Interop Workbench Kit — rules-of-engagement ingestion, canonical transcripts, and certification bundles
status: idea
domains: [finance, trading, protocols, interoperability, testing]
last_reviewed: 2026-03-06
evidence:
  - https://www.fixtrading.org/online-specification/
  - https://www.fixtrading.org/standards/fix-orchestra-online/
  - https://github.com/FIXTradingCommunity/fix-orchestra-spec
---

# Problem

Rust now has **multiple serious FIX implementation paths** — bindings around QuickFIX plus native engines and parsers such as `quickfix`, `fefix`, `fixer`, and HotFIX crates — but the ecosystem still lacks a shared **interop and certification layer**. In practice, the expensive failures are rarely “cannot parse tag=value at all”; they are:

- venue-specific Rules of Engagement drifting from baseline FIX/FIXT,
- session-behavior mismatches (reset, resend, gap fill, logon/logout edge cases),
- dialect-specific enumerations and required fields,
- counterparty onboarding that still depends on PDFs, spreadsheets, and packet captures,
- incident reports that cannot be replayed across engines.

FIX Orchestra exists precisely to make Rules of Engagement machine-readable, yet Rust lacks a cohesive crate/workspace that turns Orchestra and raw FIX transcripts into **replayable evidence** and **explainable diffs**.

# What it provides

A crate/workspace for teams that need **reliable counterparty onboarding and reproducible compatibility debugging**:

- `fix-orchestra-load` — ingest Orchestra / repository metadata into a Rust IR.
- `fix-transcript` — canonicalize FIX/FIXT session transcripts, resend flows, sequence resets, and gap fills.
- `fix-profile` — venue/counterparty profile layer for required fields, enums, timing policies, and tolerated deviations.
- `fix-replay` — deterministic replay of captured sessions against engine adapters.
- `fix-diff` — semantic diffs for message meaning, session behavior, and rules-of-engagement mismatches.
- `cargo fix-interop` — generate `*.fixbundle.zip` artifacts for certification, onboarding, and incident exchange.

# Users & user stories

- **Trading venue teams**: “Can we publish one machine-readable profile instead of a 200-page onboarding PDF?”
- **Broker / buy-side connectivity teams**: “Show the first divergence between our initiator and the venue’s expected FIX behavior.”
- **Rust FIX engine authors**: “Replay the same transcript against multiple engines and produce comparable verdicts.”
- **Support / TAM teams**: “Send one redacted bundle with transcript, profile, and verdicts instead of a week of email.”

# Prior art (and why it’s insufficient)

- `quickfix` gives Rust access to the long-lived QuickFIX substrate, but it is not a Rust-native evidence layer.
- `fefix`, `fixer`, and newer HotFIX crates show real native momentum, but they do not define a shared certification bundle or Orchestra-first workflow.
- FIX Trading Community publishes the normative protocol and Orchestra resources, but there is no default Rust workbench that joins those standards with capture, replay, and diff.

# Design goals

1. **Orchestra-first** — treat machine-readable Rules of Engagement as the primary input, not an optional extra.
2. **Session semantics matter** — diffs must understand resend, gap fill, sequence reset, heartbeats, and timing policy.
3. **Counterparty-safe bundles** — redact account IDs, ClOrdIDs, trader identifiers, and venue secrets by default.
4. **Engine pluralism** — adapt to multiple Rust FIX engines and bindings instead of declaring one winner.
5. **Boring onboarding** — make certification packs and venue profiles versionable in Git.

# Non-goals

- Not a new matching engine or OMS.
- Not a market-data plant.
- Not a universal replacement for every FIX engine.

# Architecture & API sketch

```rust
pub struct FixBundleReport {
    pub session_profile: String,
    pub transcript_hash: String,
    pub verdicts: Vec<Verdict>,
    pub divergences: Vec<Divergence>,
}

pub trait FixEngineAdapter {
    fn send(&mut self, event: CanonicalFixEvent) -> Result<(), Error>;
    fn poll(&mut self) -> Result<Vec<CanonicalFixEvent>, Error>;
}

pub fn load_orchestra(bytes: &[u8]) -> Result<OrchestraIr, Error>;
pub fn replay(bundle: &FixBundle, adapter: &mut dyn FixEngineAdapter) -> Result<FixBundleReport, Error>;
```

Bundle draft: `orchestra.xml`, `profile.toml`, `transcript.fixlog`, `canonical.jsonl`, `verdicts.json`, `redaction-map.json`, `notes.md`.

# Security / safety model

- Redact business identifiers and venue credentials by default.
- Treat inbound FIX and Orchestra files as hostile input: size limits, XML hardening, checksum/length validation, replay bounds.
- Keep “strict spec” and “accepted venue quirk” verdicts separate.

# Maintenance & governance plan

- Maintain tiny, stable IR crates and keep engine adapters separate.
- Version bundles against exact Orchestra/profile snapshots.
- Prefer venue-agnostic fixture packs first, then add opt-in venue/community packs.

# Milestones

## 0.1
- Canonical transcript IR
- Sequence/timing/session diff engine
- Redaction presets

## 0.2
- Orchestra ingestion
- Engine adapter trait + one native adapter + one QuickFIX adapter
- `cargo fix-interop replay`

## 1.0
- Stable `*.fixbundle.zip`
- Certification corpus for FIX 4.4 / FIXT session edge cases
- Machine-readable counterparty profile format with explainable verdicts

# Open questions

- How much of Orchestra should be normalized into a compact Rust IR versus preserved verbatim?
- Which session timing behaviors need deterministic simulation to be useful in CI?
- Should profile rules be Rust, CEL, or a smaller declarative DSL?

# Sources

- FIX Latest online specification: https://www.fixtrading.org/online-specification/
- FIX standards overview (incl. Orchestra): https://www.fixtrading.org/standards/
- Orchestra Online overview: https://www.fixtrading.org/standards/fix-orchestra-online/
- FIX Orchestra specification repository: https://github.com/FIXTradingCommunity/fix-orchestra-spec
- FIX Orchestra resources: https://github.com/FIXTradingCommunity/fix-orchestra
- Rust crates: https://crates.io/crates/quickfix ; https://crates.io/crates/fefix ; https://crates.io/crates/fixer ; https://crates.io/crates/hotfix-message
