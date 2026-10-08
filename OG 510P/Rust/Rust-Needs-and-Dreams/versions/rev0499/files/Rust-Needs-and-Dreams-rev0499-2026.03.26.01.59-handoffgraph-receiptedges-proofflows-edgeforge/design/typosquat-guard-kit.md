# Design: Typosquat Guard Kit (`cargo guard`, name-risk/v0)

## Goal
Make typosquatting/impersonation defenses adoptable by providing:
- a **pre-flight** CLI check (`cargo guard`) that flags suspicious dependencies,
- a portable `name-risk-report/v0` schema,
- an optional crates.io-side algorithm & UI for warnings, not hard bans.

## References (signals)
- crates.io malicious crate notification policy update (Feb 2026):  
  https://blog.rust-lang.org/2026/02/13/crates.io-malicious-crate-update/
- Automated detection methodology for typosquatting candidates (ACM poster, Aug 2025):  
  https://dl.acm.org/doi/10.1145/3708821.3735340
- Community “block near names” discussion (context + UX concerns):  
  https://www.reddit.com/r/rust/comments/1r3wa64/cratesio_an_update_to_the_malicious_crate/

## Core UX: `cargo guard`
- `cargo guard name-risk`  
  Analyze `Cargo.lock` and report crates that are close to high-value targets.
- `cargo guard diff <A> <B>`  
  Compare two reports and highlight newly introduced risks in PRs.
- `cargo guard policy check`  
  Enforce org policies (e.g., forbid dependencies within distance ≤ 2 of top-500 crates unless allowlisted).
- `cargo guard explain <crate>`  
  Show “why”: similarity features, target candidates, popularity weights, namespace hints.

## Risk model (multi-signal, low-noise by default)
Inputs:
- Name similarity metrics:
  - Levenshtein / Damerau-Levenshtein distance
  - keyboard-adjacent edits
  - homoglyph / confusable characters
  - tokenization (hyphens/underscores), pluralization
- Target weighting:
  - reverse-dep count / download rank (registry-provided)
  - org namespaces (shared prefixes)
- Context:
  - dependency introduction time (newly added this PR)
  - whether dependency is direct vs transitive
  - build-dep / proc-macro scope (higher risk)

Output:
- risk score is optional; **required**: reason codes and candidate targets.

## Artifact: `name-risk-report/v0`
Per lockfile:
- graph hash
- list of findings:
  - `crate`
  - `candidate_targets` (top K) with evidence
  - `reason_codes`:
    - `EDIT_DISTANCE_SMALL`
    - `HOMOGLYPH_CONFUSABLES`
    - `SUSPICIOUS_SUFFIX_PREFIX`
    - `TARGET_IS_HIGH_VALUE`
    - `NEW_DEP_INTRODUCED`
    - `HIGH_RISK_SCOPE_BUILD_DEP`
  - suggested actions: verify maintainer identity, pin exact version, require signatures, etc.

## Integration points
- Trust Signals Kit: ingest `name-risk-report/v0` as a signal.
- Resolve Doctor: show “risk diff” when resolution pulls a suspicious crate.
- Signed Binaries / Release Pipeline Kit: recommend stricter policies for high-risk crates.

## Evaluation plan
- Offline corpus:
  - replay historical crates.io incidents (where available)
  - evaluate false positive rates by popularity bucket
- Success criteria:
  - default mode flags *few* items on typical lockfiles, but catches obvious lookalikes.
