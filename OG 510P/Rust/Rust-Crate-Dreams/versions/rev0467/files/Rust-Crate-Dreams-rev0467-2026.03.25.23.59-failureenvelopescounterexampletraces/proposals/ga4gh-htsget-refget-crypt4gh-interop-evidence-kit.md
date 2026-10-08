---
id: P-0337
title: GA4GH htsget + refget + Crypt4GH Interop & Evidence Kit — profile-pinned genomic streaming, reference integrity checks, and redactable evidence bundles
status: idea
domains: [genomics, bioinformatics, healthcare, protocols, security, interoperability]
last_reviewed: 2026-03-06
evidence:
  - https://www.ga4gh.org/product/htsget/
  - https://ga4gh.github.io/refget/
  - https://www.ga4gh.org/product/genetic-data-encryption-crypt4gh/
  - https://github.com/ga4gh/htsget-compliance
  - https://crates.io/crates/noodles-htsget
  - https://docs.rs/crypt4gh
  - https://crates.io/crates/htsget-search
---

# Problem

Rust now has real substrate for genomic file parsing and even pieces of the GA4GH delivery stack, but the painful failures in production data sharing pipelines still sit at the seam between **range-based streaming, reference identity, and secure transport**:

- htsget services that mostly work but disagree on query, ticket, and slicing behavior,
- clients that can fetch reads or variants but cannot explain why one endpoint’s semantics drift from another’s,
- reference-sequence mismatches that only surface after expensive downstream analysis,
- Crypt4GH-encrypted flows that become operationally opaque once institutions try to share minimally reproducible bug artifacts,
- and compliance results that are hard to compare across servers, profiles, and releases.

The worthy crate contribution is an **adapter-first interop and evidence kit** that pins GA4GH delivery assumptions, normalizes service behavior, and turns genomic streaming failures into replayable, redactable bundles.

# What it provides

- `ga4gh-ir` — a canonical Rust IR for htsget capabilities, ticket responses, slices, headers, error surfaces, reference identities, and encryption/profile metadata.
- `htsget-profile` — lockfiles pinning endpoint expectations: reads vs variants, ticket shape, auth mode, allowed formats, encryption policy, and server-specific quirks.
- `refget-check` — canonical validation of sequence identities and sequence-collection references before and after streaming operations.
- `crypt4gh-adapter` — normalized handling of encrypted payload metadata, key handling hooks, and redaction-aware evidence capture.
- `ga4gh-replay` — deterministic transcript replay for htsget request/response flows with stable semantic verdicts.
- `ga4gh-diff` — semantic diffs such as “same region, different slice decomposition”, “reference digest mismatch”, or “endpoint claims CRAM but only returns BAM-compatible semantics”.
- `cargo ga4gh-evidence` — emit `*.ga4ghbundle.zip` for CI, vendor handoff, or inter-institution debugging.

# What the crate should provide other people

1. **A boring default for GA4GH streaming compatibility work** instead of ad-hoc shell scripts and private captures.
2. **One place to pin genomic delivery assumptions** across client, server, and institutional deployment profiles.
3. **Reference-integrity checks that travel with the bug report**, not as tribal knowledge.
4. **A PHI-aware evidence format** that keeps enough structure to debug failures without shipping raw patient data everywhere.
5. **A bridge between compliance suites and day-two operations** so conformance results become reusable engineering artifacts.

# Persona / who it’s for

- Bioinformatics platform engineers
- Genomics API implementers
- Clinical/research data-sharing teams
- Rust developers building on `noodles`, `htsget-search`, or `crypt4gh`
- QA and interoperability teams in regulated environments

# Users & user stories

- **Server implementer**: “Run the same region query against two htsget services and tell me whether they differ semantically or just byte-for-byte.”
- **Consumer team**: “Prove this CRAM request failure is caused by reference mismatch, not auth or index drift.”
- **Security engineer**: “Preserve enough Crypt4GH metadata to debug the exchange without leaking payload contents.”
- **Standards/conformance lead**: “Turn compliance-suite output into durable fixtures and regression bundles.”

# Prior art (and why it’s insufficient)

- GA4GH has official product/specification surfaces for **htsget**, **refget**, and **Crypt4GH**.
- The GA4GH **htsget compliance suite** already tests important parts of service behavior.
- Rust has real substrate in `noodles-htsget`, `htsget-search`, and `crypt4gh`.
- But there is still no boring-default Rust crate family for **profile pinning + reference verification + replayable evidence + redaction-aware interop bundles** across these seams.

# Design goals

1. **Adapter-first** — wrap official specs and compliance surfaces instead of inventing a parallel protocol universe.
2. **Reference-aware correctness** — refget-backed integrity checks must be first-class, not optional afterthoughts.
3. **Security-aware evidence** — encrypted and sensitive flows must still be debuggable.
4. **Semantic diagnostics over byte churn** — the findings vocabulary should explain genomic delivery failures in domain terms.
5. **Implementation neutrality** — useful whether the server is Rust, Go, Java, or Python.

# MVP surface

- Minimal types: `ServiceSnapshot`, `TicketSnapshot`, `ReferenceCheck`, `Ga4ghProfile`, `Ga4ghReport`, `ReplayTranscript`
- Minimal functions:
  - `load_service_info()`
  - `run_htsget_checks()`
  - `verify_reference()`
  - `replay_transcript()`
  - `diff_reports()`
  - `write_bundle()`
- Feature flags:
  - `htsget`
  - `refget`
  - `crypt4gh`
  - `serde`
  - `redaction`

# Compatibility story

- MVP should target the currently published **GA4GH htsget** and **refget** surfaces first, with explicit profile notes for optional capabilities.
- Crypt4GH support should stay adapter-first and metadata-focused early, not promise a universal secure-sharing platform.
- The crate should complement `noodles` and server/client implementations rather than replace them.
- MVP should intentionally avoid becoming a full clinical genomics workflow engine.

# Conformance & fixtures

- Tiny fixtures for reads and variants across BAM/CRAM/VCF/BCF paths where licensing and privacy allow.
- Reference fixtures with known digest expectations and intentional mismatch cases.
- Replay fixtures for auth failures, unsupported format negotiation, malformed tickets, and ticket-to-slice inconsistencies.
- Compliance-suite adapters so official results can be normalized into stable finding vocabularies.

# Path to boring stability

- First stabilize the profile model and semantic findings vocabulary.
- Then prove that compliance results and live transcripts can be normalized without becoming too vendor-specific.
- Freeze the bundle layout only after redaction retains enough evidence for real debugging.
- Keep encryption handling explicit and minimal until the evidence model is trusted.

# Scorecard

- Impact: 4/5
- Neglectedness: 4/5
- Feasibility: 4/5
- Adoptability: 4/5
- Sustainability: 3/5
- Differentiation: 4/5
- **Total: 23/30**

# Minimum lovable MVP

A CLI and library that load one or more htsget endpoints, pin expected service capabilities, run a region query plus refget-backed reference checks, normalize the results into stable findings, and emit a redactable `*.ga4ghbundle.zip` that can be replayed in CI.

# De-risk plan

1. Start with metadata, tickets, and reference verification before full encrypted payload workflows.
2. Reuse official compliance cases where possible.
3. Treat Crypt4GH as an evidence-aware adapter layer first.
4. Use tiny synthetic and public genomic fixtures before touching institution-specific datasets.

# Non-goals

- Not a full genomics warehouse or analysis stack.
- Not a replacement for `noodles` or raw HTS parsers.
- Not a patient-record management system.

# Architecture & API sketch

```rust
pub struct Ga4ghReport {
    pub profile_id: String,
    pub service_findings: Vec<Finding>,
    pub reference_findings: Vec<Finding>,
    pub replay_findings: Vec<Finding>,
    pub diffs: Vec<DiffFinding>,
}

pub fn run_htsget_checks(profile: &Ga4ghProfile, service: &ServiceSnapshot) -> Ga4ghReport;
pub fn verify_reference(profile: &Ga4ghProfile, sequence: &ReferenceSequence) -> Result<ReferenceCheck>;
```

Bundle draft: `profile.toml`, `service-info.json`, `tickets/`, `reference-checks.json`, `replay/`, `findings.json`, `diff.json`, `redaction-map.json`, `notes.md`.

# Security / safety model

- Default to metadata-first and transcript-first capture; payload inclusion should be opt-in.
- Redact identifiers, access tokens, and sensitive request headers by default.
- Preserve cryptographic digests and structural evidence needed for reproducibility.
- Record exact server version, validator/compliance-suite version, and profile pack version when known.

# Maintenance & governance plan

- Keep the core focused on IRs, adapters, and finding vocabularies.
- Version profile packs separately from bundle layout.
- Encourage public synthetic fixtures and public reference corpora first.
- Treat sensitive-data redaction as a release blocker, not a “later hardening” item.

# Milestones

## 0.1
- htsget service-info loader
- basic transcript capture
- refget integrity checks

## 0.2
- compliance-suite adapter
- semantic diffs
- redactable bundle writer

## 1.0
- stable `*.ga4ghbundle.zip`
- CI-ready fixture corpus
- documented policy for profile/version drift

# Open questions

- How much payload detail is actually needed for useful replay in privacy-sensitive settings?
- Should refget checks be mandatory in all profiles or only recommended for some flows?
- How much Crypt4GH support belongs in core versus optional adapters?

# Sources

- GA4GH htsget: https://www.ga4gh.org/product/htsget/
- GA4GH refget: https://ga4gh.github.io/refget/
- GA4GH Crypt4GH: https://www.ga4gh.org/product/genetic-data-encryption-crypt4gh/
- htsget compliance suite: https://github.com/ga4gh/htsget-compliance
- `noodles-htsget`: https://crates.io/crates/noodles-htsget
- `htsget-search`: https://crates.io/crates/htsget-search
- `crypt4gh`: https://docs.rs/crypt4gh
