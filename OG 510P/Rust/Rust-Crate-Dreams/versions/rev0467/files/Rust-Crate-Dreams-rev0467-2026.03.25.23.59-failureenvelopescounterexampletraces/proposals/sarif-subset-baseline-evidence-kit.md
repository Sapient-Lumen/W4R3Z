---
id: P-0367
title: SARIF 2.1.0 Subset + Baseline + Evidence Kit — subset locks, fingerprint-normalized diffs, and replayable static-analysis bundles
status: idea
domains: [security, static-analysis, devtools, ci, standards, interoperability, validation, tooling]
last_reviewed: 2026-03-06
evidence:
  - https://docs.oasis-open.org/sarif/sarif/v2.1.0/sarif-v2.1.0.html
  - https://docs.github.com/en/code-security/reference/code-scanning/sarif-files/sarif-support-for-code-scanning
  - https://docs.github.com/en/code-security/how-tos/scan-code-for-vulnerabilities/integrate-with-existing-tools/uploading-a-sarif-file-to-github
  - https://github.blog/changelog/2025-07-21-code-scanning-will-stop-combining-multiple-sarif-runs-uploaded-in-the-same-sarif-file/
  - https://crates.io/crates/sarif_rust
  - https://docs.rs/serde-sarif
---

# Problem

Rust can already serialize and deserialize SARIF, but operational pain rarely comes from “can I parse the JSON?” It shows up at the seam between:

- full SARIF 2.1.0 versus the narrower subsets that downstream platforms actually accept,
- rule identity, fingerprints, and baseline stability across runs,
- multiple-tool or multiple-run packaging decisions,
- suppression, deduplication, and alert lifecycle semantics,
- and bug reports that arrive as “GitHub/Azure/our triage portal handled this SARIF strangely” with no portable reproduction artifact.

The missing Rust contribution is not another scanner. It is a **subset-and-evidence workbench** that makes SARIF exchange failures reproducible, explainable, and small enough to share.

# What it provides

- `sarif-lock` — lockfiles pinning the intended SARIF surface: version, allowed properties, rule-id policy, baseline policy, fingerprint requirements, and target-platform subset.
- `sarif-irx` — a neutral IR for results, rules, locations, fingerprints, suppressions, logical runs, and platform-specific findings.
- `subset-check` — validate a SARIF file against a named target profile such as “portable core”, “GitHub code scanning subset”, or a team-defined house profile.
- `baseline-diff` — semantic diffs such as “same result, different fingerprint identity”, “same rule, changed location semantics”, or “multi-run bundle rejected because platform expects split uploads”.
- `cargo sarif-evidence` — emits `*.sarifbundle.zip` with original SARIF, normalized IR, profile lock, subset findings, fingerprint analysis, redaction maps, and notes.

# What the crate should provide other people

1. **A boring default artifact for SARIF compatibility bugs**.
2. **Subset locks** so teams can say what flavor of SARIF they actually target rather than waving at the whole spec.
3. **Stable baseline and deduplication analysis** so alert churn becomes explainable.
4. **Portable replay bundles** for CI failures, support tickets, and scanner integration work.
5. **A bridge from Rust SARIF types to evidence-grade code-scanning workflows**.

# Persona / who it’s for

- Authors of Rust security scanners, linters, SAST tools, and secret scanners
- Platform teams integrating non-CodeQL tools with GitHub or similar code-scanning backends
- DevSecOps teams trying to keep findings stable across runs
- Maintainers of SARIF post-processing, upload, or triage pipelines

# Users & user stories

- **Scanner author**: “Tell me whether my SARIF is valid in general, valid for GitHub, or only valid for my own pipeline.”
- **Platform engineer**: “Why did these alerts duplicate across runs even though the source finding did not change?”
- **Security maintainer**: “Split the semantic diff between real finding changes and presentation-only churn.”
- **Support engineer**: “Ship one compact bundle that reproduces why this upload was accepted, rejected, or normalized differently.”

# Prior art (and why it’s insufficient)

- OASIS defines SARIF 2.1.0 as the standard interchange format.
- GitHub documents a supported subset of SARIF 2.1.0 and specific guidance around `partialFingerprints`.
- Rust has usable crates such as `sarif_rust` and `serde-sarif`.
- But Rust still lacks a boring-default crate for **subset locks + baseline/fingerprint normalization + semantic diffs + portable evidence bundles**.

# Design goals

1. **Subset-first** — treat platform and house-profile subsets as first-class, not as afterthoughts.
2. **Identity-aware** — rule IDs, locations, fingerprints, and suppression reasons must be comparable in stable ways.
3. **Platform-neutral core** — adapters may speak GitHub or other consumers, but the lockfile and IR should not collapse into one vendor.
4. **Deterministic artifacts** — same input and same normalization policy should yield stable bundles and diffs.
5. **Redaction-safe** — sensitive paths, snippets, or proprietary rule metadata should be shareable safely.

# MVP surface

- Minimal types: `SarifLock`, `TargetProfile`, `SarifBundle`, `SubsetFinding`, `BaselineDiffFinding`
- Minimal functions:
  - `normalize_run()`
  - `check_profile()`
  - `analyze_fingerprints()`
  - `diff_baselines()`
  - `write_bundle()`
- Feature flags:
  - `github-profile`
  - `portable-core`
  - `redaction`
  - `path-remap`

# Compatibility story

- MVP should support SARIF 2.1.0 documents but make target subsets explicit.
- The crate should complement parser/serde crates rather than replace them.
- Vendor-specific checks should live in adapter/profile packs over a stable core IR and bundle schema.
- Multi-run handling should remain explicit because different consumers make different assumptions.

# Conformance & fixtures

- Tiny SARIF fixtures for valid core documents, missing fingerprints, unstable fingerprints, suppression churn, and multi-run edge cases.
- Goldens for “same finding, different path roots”, “same rule, different dedupe identity”, and “valid SARIF, rejected target subset”.
- Repro bundles for upload-oriented workflows, including path remapping and snippet redaction.
- Public profile packs for at least a portable core and GitHub-oriented surface.

# Path to boring stability

- Stabilize the lockfile, normalized IR, and diff semantics before chasing many platform adapters.
- Start with one serious target profile rather than five partial ones.
- Treat alert identity and baseline churn as a first-class UX problem.
- Keep bundles tiny and reviewable so support and CI users actually adopt them.

# Scorecard

- Impact: 5/5
- Neglectedness: 4/5
- Feasibility: 4/5
- Adoptability: 5/5
- Sustainability: 4/5
- Differentiation: 4/5
- **Total: 26/30**

# Minimum lovable MVP

A library and CLI that validate one SARIF file against a portable core plus a GitHub-oriented profile, analyze fingerprint/baseline stability, and emit a compact `*.sarifbundle.zip` with normalized findings and semantic diffs.

# De-risk plan

1. Start with normalization + profile validation before building fancy upload adapters.
2. Keep fingerprint analysis explicit and well-documented from day one.
3. Use tiny public fixtures that target real downstream quirks.
4. Make redaction and path-remapping policies stable early so bundles are safe to share.

# Non-goals

- Not a static-analysis engine.
- Not a vulnerability database.
- Not a generic code-scanning SaaS.
- Not a replacement for every platform’s own UI or ingestion API.

# Architecture & API sketch

```rust
pub struct SarifLock {
    pub version: String,
    pub target_profile: String,
    pub fingerprint_policy: FingerprintPolicy,
}

pub fn check_profile(lock: &SarifLock, doc: &SarifDocument) -> Result<SarifReport>;
pub fn diff_baselines(old: &SarifReport, new: &SarifReport) -> BaselineDiff;
```

Bundle draft: `profile.toml`, `input.sarif`, `normalized.json`, `report.json`, `diff.json`, `redaction-map.json`, `notes.md`.

# Security / safety model

- Treat SARIF input as untrusted data.
- Support redaction of file paths, code snippets, and proprietary rule metadata.
- Record exact normalization and profile versions in every bundle.
- Keep bundle outputs deterministic enough for CI and issue-tracker review.

# Maintenance & governance plan

- Keep the core centered on profiles, normalized IR, diffs, and bundle format.
- Version vendor-specific profile packs separately where needed.
- Publish a small public fixture corpus focused on identity and baseline seams.
- Avoid coupling the project to one scanner vendor or one code-hosting platform.

# Milestones

## 0.1
- profile lockfile
- normalization pass
- single-document subset report

## 0.2
- baseline diffing
- fingerprint analysis
- redaction support

## 1.0
- stable `*.sarifbundle.zip`
- public profile packs
- documented compatibility policy for supported target subsets

# Open questions

- What is the smallest “portable SARIF core” that still feels worth standardizing in practice?
- Which fingerprint policies are stable enough to encode in a long-lived lockfile?
- How much multi-run semantics belongs in the stable core versus adapter packs?

# Sources

- OASIS SARIF 2.1.0: https://docs.oasis-open.org/sarif/sarif/v2.1.0/sarif-v2.1.0.html
- GitHub SARIF support for code scanning: https://docs.github.com/en/code-security/reference/code-scanning/sarif-files/sarif-support-for-code-scanning
- Uploading a SARIF file to GitHub: https://docs.github.com/en/code-security/how-tos/scan-code-for-vulnerabilities/integrate-with-existing-tools/uploading-a-sarif-file-to-github
- GitHub changelog on multi-run SARIF handling: https://github.blog/changelog/2025-07-21-code-scanning-will-stop-combining-multiple-sarif-runs-uploaded-in-the-same-sarif-file/
- `sarif_rust`: https://crates.io/crates/sarif_rust
- `serde-sarif`: https://docs.rs/serde-sarif
