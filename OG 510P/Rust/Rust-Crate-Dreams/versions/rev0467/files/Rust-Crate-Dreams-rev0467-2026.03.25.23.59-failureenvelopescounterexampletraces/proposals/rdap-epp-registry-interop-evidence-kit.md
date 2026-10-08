---
id: P-0304
title: RDAP + EPP Registry Interop & Evidence Kit — registrar/registry profile packs, canonical exchanges, and reproducible delegation bundles
status: idea
domains: [internet-infrastructure, dns, registries, security, interoperability]
last_reviewed: 2026-03-06
evidence:
  - https://www.rfc-editor.org/rfc/rfc9083.html
  - https://www.icann.org/resources/pages/rdap-operational-profile-2016-07-26-en
  - https://www.icann.org/resources/registry-system-testing-v2.0
---

# Problem

The registry/registrar world is standards-heavy and operationally unforgiving. Rust now has real RDAP momentum — ICANN-sponsored crates such as `icann-rdap-common`, `icann-rdap-client`, and `icann-rdap-srv` exist — plus EPP client substrate. But the missing layer is still the painful one:

- profile pinning for registry/registrar expectations,
- reproducible EPP/RDAP exchange traces,
- extension-awareness,
- cross-checking publication data against provisioning behavior,
- evidence bundles for onboarding, incident response, and registry testing.

This is especially timely because RDAP keeps evolving via REGEXT work and ICANN still centers operational profiles and automated registry testing. The crate gap is best framed as a **registry interop workbench**, not merely “another RDAP parser.”

# What it provides

- `rdap-profile` — pin RDAP profiles, response extensions, paging/search capabilities, and registry policy assumptions.
- `epp-profile` — pin object mappings, extensions, status-code expectations, and registry-specific workflows.
- `registry-canon` — canonical IR for EPP sessions, RDAP responses, object state transitions, and publication snapshots.
- `registry-replay` — deterministic replay for create/update/transfer/delete/query flows.
- `registry-diff` — semantic diffs between provisioned state and published state, including status and extension mismatches.
- `cargo registry-interop` — emit `*.registrybundle.zip` for onboarding, dispute handling, and regression testing.

# What the crate should provide other people

1. **A single evidence format** spanning both provisioning and publication surfaces.
2. **Profile pinning** for registry-specific extension behavior and operational rules.
3. **Replayable onboarding packs** for registrars and backend service providers.
4. **Explainable diffs** when EPP succeeded but RDAP publication is missing, stale, or profile-noncompliant.
5. **Adapter hooks** for ICANN Rust RDAP crates and existing EPP client libraries.

# Users & user stories

- **Registry operators**: “Prove our RDAP publication matches our registry state after this EPP transaction sequence.”
- **Registrars**: “Replay the exact failing transfer/contact update workflow against staging and production.”
- **Backend registry service providers**: “Generate evidence artifacts aligned with automated registry testing expectations.”
- **Security / incident teams**: “Share one redactable bundle instead of raw registrar logs and screenshots.”

# Prior art (and why it’s insufficient)

- ICANN’s Rust RDAP ecosystem is real substrate and a strong signal that Rust belongs here.
- RFC 9083 and related standards define data structures, while ICANN publishes operational profile and testing guidance.
- Existing pieces do not yet create a default **EPP + RDAP + publication-state evidence layer**.

# Design goals

1. **Provisioning/publication linkage** — EPP and RDAP should be testable together.
2. **Extension-aware** — registry-specific extensions must be first-class.
3. **Automation-friendly** — fit pre-delegation, regression, and staging workflows.
4. **Redactable but auditable** — preserve object/state evidence while suppressing sensitive contacts and auth info.
5. **IETF/ICANN drift visibility** — make evolving profiles and extension versions explicit.

# Non-goals

- Not a full registry platform.
- Not a DNS zone-serving system.
- Not a wholesale replacement for ICANN’s own test infrastructure.

# Architecture & API sketch

```rust
pub struct RegistryInteropReport {
    pub rdap_profile: String,
    pub epp_profile: String,
    pub verdicts: Vec<Verdict>,
    pub state_diffs: Vec<StateDiff>,
}

pub trait RegistryAdapter {
    fn epp(&mut self, frame: CanonicalEppFrame) -> Result<CanonicalEppEvent, Error>;
    fn rdap(&mut self, req: CanonicalRdapRequest) -> Result<CanonicalRdapResponse, Error>;
}
```

Bundle draft: `rdap-profile.toml`, `epp-profile.toml`, `session.jsonl`, `publication-snapshots.json`, `state-diff.json`, `redaction-map.json`, `verdicts.json`, `notes.md`.

# Security / safety model

- Default redaction for authInfo, contact PII, registrar internal IDs, and unpublished metadata.
- Support differentiated views for vendor exchange versus internal full-fidelity storage.
- Treat XML/JSON parsing and extension handling as hostile-input surfaces.

# Maintenance & governance plan

- Keep canonical IR and profile formats independent of any one registry operator.
- Track RFC and ICANN-profile assumptions in lockfiles.
- Encourage fixture packs for generic flows first, then operator-specific packs as add-ons.

# Milestones

## 0.1
- Canonical EPP/RDAP IR
- Basic replay harness
- Publication-versus-provisioning diff model

## 0.2
- Profile packs for common flows
- Extension-aware diffs
- `cargo registry-interop replay`

## 1.0
- Stable `*.registrybundle.zip`
- Onboarding and automated-regression scenario packs
- Clear mapping to RDAP/EPP/profile failures

# Open questions

- How should the MVP boundary balance gTLD-centric profiles versus broader RDAP/EPP use?
- Which extensions deserve first-class support rather than adapter-specific metadata?
- How should eventual consistency between provisioning and publication be modeled in verdicts?

# Sources

- RFC 9083: https://www.rfc-editor.org/rfc/rfc9083.html
- RFC 9536 reverse search extension: https://www.rfc-editor.org/rfc/rfc9536.html
- Example recent EPP extension RFC 9873: https://www.rfc-editor.org/rfc/rfc9873.html
- ICANN RDAP operational profile: https://www.icann.org/resources/pages/rdap-operational-profile-2016-07-26-en
- ICANN Registry System Testing v2.0: https://www.icann.org/resources/registry-system-testing-v2.0
- ICANN RDAP Rust project: https://github.com/icann/icann-rdap
- Rust crates: https://crates.io/crates/icann-rdap-common ; https://crates.io/crates/icann-rdap-client ; https://crates.io/crates/icann-rdap-srv ; https://crates.io/crates/epp-client
