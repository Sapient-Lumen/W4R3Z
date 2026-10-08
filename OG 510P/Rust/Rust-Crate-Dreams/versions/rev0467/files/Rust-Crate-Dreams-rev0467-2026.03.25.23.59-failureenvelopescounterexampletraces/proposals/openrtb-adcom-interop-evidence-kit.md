---
id: P-0292
title: OpenRTB 2.6 + AdCOM Interop & Evidence Kit — canonical bid traces + profile-as-code + replay/diff
status: idea
domains: [adtech, interop, protocols, testing, data]
last_reviewed: 2026-03-06
evidence:
  - https://iabtechlab.com/standards/openrtb/
  - https://iabtechlab.com/wp-content/uploads/2022/04/OpenRTB-2-6_FINAL.pdf
  - https://github.com/InteractiveAdvertisingBureau/openrtb2.x
---

# Problem

OpenRTB is a huge economic protocol surface, but Rust mostly has **schema crates**, not a serious **interop workbench**.
OpenRTB 2.6 moved enumerations into **AdCOM** and the current 2.x spec now sees ongoing non-breaking monthly updates, which makes drift likely unless implementations pin and test against concrete snapshots. Existing Rust crates (`iab`, `iab-specs`, `openrtb`, `openrtb2`) help with types, but they do not provide a standard way to:

- replay bidder/exchange traces,
- diff semantic mismatches,
- pin list/enumeration snapshots,
- encode marketplace-specific profiles,
- ship redactable incident bundles for support and certification.

# What it provides

A crate/workspace other people can rely on for **production-grade compatibility work**:

- `openrtb-evidence` — canonical IR for request/response traces, redaction, and semantic diffs.
- `openrtb-profile` — profile-as-code layer for exchange/bidder house rules, required fields, enum freezes, and warnings.
- `openrtb-replay` — deterministic replay of captured bid traffic against adapters.
- `openrtb-fixtures` — conformance corpus for CTV/video/native/privacy edge cases.
- `cargo openrtb` — CLI to capture, normalize, lint, diff, and bundle incidents into `*.rtbbundle.zip`.

# Users & user stories

- **DSP / bidder teams**: “Why did exchange A reject this bid but exchange B accept it?”
- **SSP / exchange teams**: “Show me the first semantic divergence between our interpretation and the buyer’s.”
- **CTV marketplace teams**: “Pin the exact enum snapshot and object expectations we certify against.”
- **Consultancies / SRE / TAMs**: “Send one redacted artifact instead of a week of screenshots and hand-edited JSON.”

# Prior art (and why it’s insufficient)

- `iab` and `iab-specs` provide typed structures for OpenRTB/AdCOM, which is useful substrate, but not incident bundles, replay, or semantic profile validation.
- `openrtb` / `openrtb2` focus on older 2.5-era type surfaces.
- Google’s Authorized Buyers OpenRTB proto is valuable field context, but it is one large implementation-specific mapping, not a Rust-native interop harness.

# Design goals

1. **Semantic, not textual, diffs** — compare meaning, not raw JSON ordering.
2. **Profile-as-code** — marketplace and region-specific constraints must be declarative and versioned.
3. **Privacy-safe by default** — PII / IDs / URLs / IP ranges redacted or tokenized.
4. **Fast fixture feedback** — easy CI use for bidder/exchange compatibility checks.
5. **Composable adapters** — works with existing Rust OpenRTB crates rather than replacing them.

# Non-goals

- Not a bidder, exchange, or auction engine.
- Not a full business-rules product for campaign management.
- Not a replacement for bespoke marketplace contracts.

# Architecture & API sketch

```rust
pub struct BundleReport {
    pub schema_version: String,
    pub profile_id: String,
    pub verdicts: Vec<Verdict>,
    pub divergences: Vec<Divergence>,
}

pub trait RtbAdapter {
    fn decode_request(&self, bytes: &[u8]) -> Result<BidRequestIr, DecodeError>;
    fn encode_response(&self, ir: &BidResponseIr) -> Result<Vec<u8>, EncodeError>;
}

pub trait ProfileRule {
    fn check(&self, trace: &TraceIr, out: &mut Vec<Verdict>);
}
```

Bundle draft: `bundle.toml`, `trace.jsonl`, `profile.lock`, `verdicts.json`, `redaction-map.json`, `notes.md`.

# Security / safety model

- Redact device IDs, IPs, URLs, user IDs, deal IDs, and billing identifiers by default.
- Require explicit opt-in to preserve raw request payloads.
- Cap bundle size and fixture execution time to avoid hostile traffic captures becoming denial-of-service inputs.
- Separate “strict conformance” from “real-world lenient parsing” verdicts.

# Maintenance & governance plan

- Keep the core schema tiny and additive.
- Ship an upstream fixture contribution guide per marketplace/profile.
- Maintain official adapters for only a few major Rust crates; accept third-party adapters for the rest.
- Publish frozen enum snapshots keyed to OpenRTB/AdCOM release dates.

# Milestones

## 0.1
- Canonical IR for bid request/response traces
- Redaction presets
- JSON semantic diff

## 0.2
- Profile-as-code validator
- Exchange/bidder fixture packs
- `cargo openrtb diff`

## 1.0
- Stable `*.rtbbundle.zip`
- Adapter suite for the main Rust type crates
- Corpus covering CTV, native, privacy, and policy edge cases

# Open questions

- How strict should enum pinning be when the 2.x repo updates monthly?
- Which privacy-preserving tokenization defaults are acceptable for incident sharing across companies?
- Should house rules be authored in Rust, CEL/Rego, or a simpler bespoke rule DSL?

# Sources

- IAB Tech Lab OpenRTB standard page: https://iabtechlab.com/standards/openrtb/
- OpenRTB 2.6 spec: https://iabtechlab.com/wp-content/uploads/2022/04/OpenRTB-2-6_FINAL.pdf
- OpenRTB 2.x repository (current monthly-updated line): https://github.com/InteractiveAdvertisingBureau/openrtb2.x
- OpenRTB 2.6 markdown: https://github.com/InteractiveAdvertisingBureau/openrtb2.x/blob/main/2.6.md
- Authorized Buyers OpenRTB proto mapping: https://developers.google.com/authorized-buyers/rtb/downloads/openrtb-proto
- Rust crates: https://crates.io/crates/iab ; https://crates.io/crates/iab-specs ; https://crates.io/crates/openrtb ; https://crates.io/crates/openrtb2
