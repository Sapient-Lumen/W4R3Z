---
id: P-0320
title: HLS + Low-Latency HLS + CMAF Interop & Evidence Kit — playlist/profile lockfiles, rendition diffs, and replayable streaming bug bundles
status: idea
domains: [media, streaming, hls, ll-hls, cmaf, interoperability]
last_reviewed: 2026-03-06
evidence:
  - https://www.rfc-editor.org/rfc/rfc8216.html
  - https://datatracker.ietf.org/doc/draft-pantos-hls-rfc8216bis/
  - https://developer.apple.com/streaming/
  - https://developer.apple.com/documentation/http-live-streaming/enabling-low-latency-http-live-streaming-hls
  - https://crates.io/crates/m3u8-rs
  - https://crates.io/crates/hls_client
  - https://docs.rs/quick-m3u8
---

# Problem

Rust has enough HLS substrate today that another parser alone is not the main missing contribution. The painful problems are operational and semantic:

- master/media playlist drift,
- rendition mismatches,
- discontinuity and timeline bugs,
- low-latency behavior that “sort of works” until a player stalls,
- and incident reports that still move around as copied playlists and vague playback complaints.

The worthy crate contribution is a **HLS / LL-HLS / CMAF interop and evidence kit** that turns playlist behavior into profile-pinned, replayable, diffable artifacts.

# What it provides

- `hls-ir` — canonical IR for master/media playlists, variant/rendition relationships, segment and part timelines, discontinuities, keys, and delivery assumptions.
- `hls-profile` — lockfiles for RFC 8216 / 8216bis assumptions, Apple authoring expectations, LL-HLS/CMAF behavior, and accepted tag surface.
- `hls-verify` — semantic checks for playlist/version consistency, target durations, discontinuity alignment, rendition groups, and low-latency constraints.
- `hls-replay` — deterministic replay of playlist refresh sequences and segment/part fetch behavior.
- `hls-diff` — explainable diffs: “audio rendition group changed”, “part hold-back violated profile”, “target duration drifted”, “variant bitrate ladder became inconsistent”.
- `cargo hls` — emit `*.hlsbundle.zip` for encoder/packager regressions, CDN bugs, and player compatibility investigations.

# What the crate should provide other people

1. **A portable streaming bug artifact** instead of copied `.m3u8` text and hand-written notes.
2. **Profile lockfiles** that state exactly which HLS / LL-HLS rules a workflow expects.
3. **Timeline-aware diffs** for playlist and rendition changes.
4. **Replayable refresh/fetch traces** for CI and regression testing.
5. **A shared interoperability layer** above existing Rust playlist parsers and clients.

# Users & user stories

- **Streaming platform engineers**: “Show me the first refresh where the live edge became invalid.”
- **Packager / encoder teams**: “Compare yesterday’s output against the last known-good ladder semantically.”
- **Player developers**: “Replay the exact LL-HLS refresh sequence that caused rebuffering.”
- **CDN / operations teams**: “Archive a minimal, reproducible bundle for a customer playback incident.”

# Prior art (and why it’s insufficient)

- RFC 8216 and the active 8216bis draft define the normative core and its evolution.
- Apple publishes current HLS and low-latency guidance, which means profile-aware tooling can be anchored to real deployment expectations.
- Rust already has playlist parsers and clients (`m3u8-rs`, `quick-m3u8`, `hls_client`).
- But those crates do not yet provide a shared **profile pinning + replay + semantic diff + evidence bundle** workflow.

# Design goals

1. **Timeline-aware** — HLS bugs are often temporal, not merely syntactic.
2. **Low-latency realistic** — partial segments, hold-backs, and refresh behavior must be first-class.
3. **Profile-pinned** — exact rule surfaces must be explicit.
4. **Artifact-first** — support CI, vendor escalations, and bug archives.
5. **Implementation-neutral** — useful to parsers, players, packagers, and observability tools.

# Non-goals

- Not a media player.
- Not a transcoder/encoder.
- Not a DRM platform.

# Architecture & API sketch

```rust
pub struct HlsReport {
    pub profile_id: String,
    pub verdicts: Vec<Verdict>,
    pub playlist_findings: Vec<PlaylistFinding>,
    pub timing_findings: Vec<TimingFinding>,
    pub rendition_findings: Vec<RenditionFinding>,
}

pub fn verify_session(profile: &HlsProfile, session: &HlsSession) -> HlsReport;
```

Bundle draft: `profile.toml`, `playlists/*.m3u8`, `fetch-log.jsonl`, `segments/index.json`, `verdicts.json`, `diff.json`, `redaction-map.json`, `notes.md`.

# Security / safety model

- Support redaction of signed URLs, tokens, origin hostnames, and DRM-adjacent identifiers.
- Keep media bytes optional; prefer metadata-first bundles.
- Bound long-running live capture sizes.
- Record exact profile, parser, and normalizer versions for reproducibility.

# Maintenance & governance plan

- Pin exact RFC/draft and Apple-authoring assumptions in every fixture pack.
- Publish scenario packs for live-edge regressions, discontinuities, ladder drift, subtitle/audio mismatches, and LL-HLS timing problems.
- Keep IR flexible enough to represent both MPEG-TS and CMAF-oriented workflows.

# Milestones

## 0.1
- Canonical HLS IR
- Profile lockfiles
- Structural + semantic verification and bundle format

## 0.2
- Live refresh replay
- LL-HLS timing checks
- Timeline and rendition diffs

## 1.0
- Stable `*.hlsbundle.zip`
- Adapter layer for multiple Rust parsers/clients
- CI-ready packager/player compatibility workflows

# Open questions

- How much segment-byte inspection belongs in MVP versus optional adapters?
- Should DASH/CMAF overlap remain explicitly out of scope, except where needed for LL-HLS semantics?
- Which Apple-authoring checks can be normalized without becoming too proprietary?

# Sources

- RFC 8216: https://www.rfc-editor.org/rfc/rfc8216.html
- HLS 2nd Edition draft (`rfc8216bis`): https://datatracker.ietf.org/doc/draft-pantos-hls-rfc8216bis/
- Apple HLS overview: https://developer.apple.com/streaming/
- Apple low-latency HLS guidance: https://developer.apple.com/documentation/http-live-streaming/enabling-low-latency-http-live-streaming-hls
- `m3u8-rs`: https://crates.io/crates/m3u8-rs
- `hls_client`: https://crates.io/crates/hls_client
- `quick-m3u8`: https://docs.rs/quick-m3u8
