---
id: P-0351
title: MPEG-DASH + DASH-IF Conformance & Evidence Kit — MPD/segment profile locks, validator wrapping, and replayable streaming bug bundles
status: idea
domains: [streaming-media, video, protocols, interoperability, testing]
last_reviewed: 2026-03-06
evidence:
  - https://www.mpeg.org/standards/MPEG-DASH/
  - https://dashif.org/tools/conformance/
  - https://github.com/Dash-Industry-Forum/DASH-IF-Conformance
  - https://docs.rs/dash-mpd
  - https://docs.rs/crate/dash-mpd-cli/latest
---

# Problem

Rust can already parse DASH manifests and even download streams, while DASH-IF publishes a serious conformance surface. But streaming failures in production still live at the seam between **MPD semantics, segment timing, and profile assumptions**:

- a manifest parses fine but still fails due to alignment, timing, or profile drift,
- teams can run the conformance tool but cannot normalize its findings into a stable artifact for CI or vendor handoff,
- changes in packagers or encoders create subtle segment or MPD regressions that are hard to diff semantically,
- and support cases still require access to private streams rather than minimized, replayable evidence.

The missing Rust contribution is a **validator-wrapping conformance and evidence kit** for DASH workflows, not another player.

# What it provides

- `dash-ir` — a canonical Rust IR for MPDs, periods/adaptation sets/representations, profile flags, timing assumptions, and selected segment metadata.
- `dash-profile` — lockfiles pinning expected profiles, codecs, timelines, segment alignment rules, manifest constraints, and environment quirks.
- `dashif-adapter` — normalized import of DASH-IF Conformance results into stable Rust findings.
- `segment-check` — lightweight checks over segment timing, availability, and representation alignment for sampled windows.
- `dash-diff` — semantic diffs such as “same manifest shape, changed timeline behavior”, “new representation missing alignment”, or “validator verdict drift after packager upgrade”.
- `cargo dash-evidence` — emit `*.dashbundle.zip` for CI, CDN/vendor debugging, or player/packager support cases.

# What the crate should provide other people

1. **A boring default artifact for DASH compatibility bugs**.
2. **One place to pin MPD and segment assumptions in Git**.
3. **A bridge from official conformance output to reusable CI fixtures**.
4. **Semantic diffs across encoder/packager changes**.
5. **Small-share evidence bundles** that help when full streams cannot be shared.

# Persona / who it’s for

- Streaming platform engineers
- Player and manifest-tool authors
- Encoder/packager QA teams
- CDN/integration engineers
- Rust developers building media tooling

# Users & user stories

- **Packager maintainer**: “Show me whether the regression is in MPD structure, timing semantics, or representation alignment.”
- **Player team**: “Normalize DASH-IF findings and add a few transport/segment checks into one evidence bundle.”
- **CI owner**: “Gate packager upgrades on stable semantic findings instead of handwritten dashboard checks.”
- **Vendor integrator**: “Send a small bug bundle that proves a private stream fails on conformance-critical timing issues.”

# Prior art (and why it’s insufficient)

- MPEG maintains the standards family for **MPEG-DASH**.
- DASH-IF provides a public **Conformance Validator** and open-source conformance software.
- Rust has real substrate in `dash-mpd` and `dash-mpd-cli`.
- But there is still no boring-default Rust crate family for **profile lockfiles + conformance normalization + segment-aware semantic diffs + portable evidence bundles**.

# Design goals

1. **Conformance-first** — align with official DASH-IF validation surfaces rather than bypass them.
2. **Manifest-plus-segment correctness** — MPD parsing alone is not enough.
3. **Privacy-aware evidence** — support minimized bundles for private streams.
4. **Semantic diffs** — findings should survive packager and validator version churn.
5. **Tool neutrality** — useful whether the downstream player is browser, TV stack, or custom app.

# MVP surface

- Minimal types: `MpdSnapshot`, `SegmentSnapshot`, `DashProfile`, `DashReport`, `DiffFinding`
- Minimal functions:
  - `load_mpd()`
  - `run_conformance()`
  - `sample_segments()`
  - `diff_reports()`
  - `write_bundle()`
- Feature flags:
  - `dashif`
  - `segments`
  - `serde`
  - `redaction`

# Compatibility story

- MVP should target generic **MPEG-DASH** plus the public **DASH-IF** conformance surface first.
- This proposal should stay distinct from HLS-focused work: DASH-specific MPD and segment semantics deserve their own lockfiles and findings model.
- The crate should complement players and packagers, not become one.
- Environment-specific policy packs can remain optional.

# Conformance & fixtures

- Tiny public MPDs with a few segments and known alignment/timing cases.
- Goldens for missing segment, bad alignment, stale manifest timing, and validator-verdict drift.
- Sampled-segment fixtures that avoid large private media payloads.
- Normalizers for official conformance tool output.

# Path to boring stability

- Stabilize MPD/profile IR and findings vocabulary before broadening media checks.
- Keep early segment sampling bounded and deterministic.
- Freeze bundle layout only after it works for CI and vendor handoff.
- Add environment-specific overlays after the core model matures.

# Scorecard

- Impact: 4/5
- Neglectedness: 3/5
- Feasibility: 4/5
- Adoptability: 4/5
- Sustainability: 4/5
- Differentiation: 4/5
- **Total: 23/30**

# Minimum lovable MVP

A CLI and library that load an MPD, run DASH-IF conformance checks, sample key segments, normalize the results into stable findings, and emit a compact `*.dashbundle.zip`.

# De-risk plan

1. Start with MPDs plus bounded segment samples.
2. Use only public miniature fixtures in the initial corpus.
3. Normalize official findings before inventing new rule families.
4. Keep environment-specific assumptions out of core.

# Non-goals

- Not a video player.
- Not a full encoder/packager stack.
- Not a DRM system.

# Architecture & API sketch

```rust
pub struct DashReport {
    pub profile_id: String,
    pub conformance_findings: Vec<Finding>,
    pub segment_findings: Vec<Finding>,
    pub diffs: Vec<DiffFinding>,
}

pub fn run_conformance(profile: &DashProfile, mpd: &MpdSnapshot) -> Result<DashReport>;
pub fn sample_segments(profile: &DashProfile, mpd: &MpdSnapshot) -> Result<Vec<Finding>>;
```

Bundle draft: `profile.toml`, `mpd.xml`, `conformance.json`, `segments.json`, `diff.json`, `redaction-map.json`, `notes.md`.

# Security / safety model

- Treat MPDs and segments as untrusted inputs.
- Support URL/token redaction in bundles.
- Default to sampled segment metadata rather than full media inclusion.
- Record exact validator version and profile-pack version.

# Maintenance & governance plan

- Keep core focused on IRs, validators, and bundle formats.
- Version profile packs separately.
- Grow a small public corpus for CI and packager regression testing.
- Avoid coupling the crate to one playback stack.

# Milestones

## 0.1
- MPD loader
- DASH-IF adapter
- bundle writer

## 0.2
- segment sampling checks
- semantic diffs
- profile packs

## 1.0
- stable `*.dashbundle.zip`
- public fixture corpus
- documented policy for validator/profile drift

# Open questions

- Which segment-level checks belong in core versus adapters?
- How should profile packs represent environment-specific rules without becoming too vendor-specific?
- What minimum media metadata is enough for useful repro on private streams?

# Sources

- MPEG-DASH overview: https://www.mpeg.org/standards/MPEG-DASH/
- DASH-IF conformance tool: https://dashif.org/tools/conformance/
- DASH-IF conformance software repo: https://github.com/Dash-Industry-Forum/DASH-IF-Conformance
- `dash-mpd`: https://docs.rs/dash-mpd
- `dash-mpd-cli`: https://docs.rs/crate/dash-mpd-cli/latest
