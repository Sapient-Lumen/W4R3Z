# Design: Lifecycle Ledger Kit (`cargo lifecycle`, `lifecycle-pack/v0`)

## Goal
Define a portable contract for declaring, checking, diffing, and publishing crate lifecycle facts: maintenance posture, supported version windows, successor relationships, maintainer-help / handoff consent, and visible maintenance evidence.

This should **not** replace crates.io ownership policy, RustSec, or trust/policy tooling.
It should make them compose better and stop forcing lifecycle meaning into channels built for security incidents, README prose, or repo-activity heuristics.

## References (signals)
- The Rust Foundation Maintainer Fund work explicitly frames maintenance as critical, often invisible labor and seeks ways to recognize and sustain it.
  https://blog.rust-lang.org/inside-rust/2026/01/12/what-is-maintenance-anyway/
- crates.io now surfaces a Security tab and richer publish/security UX, proving the registry is already evolving toward more dependency-selection-time health information.
  https://blog.rust-lang.org/2026/01/21/crates-io-development-update/
- crates.io’s 2026 malicious-crate notification update shifts most malware communication to RustSec advisories, which is sensible security hygiene and also a reminder not to overload security channels with ordinary lifecycle meaning.
  https://blog.rust-lang.org/2026/02/13/crates.io-malicious-crate-update/
- Cargo still defines a `[badges].maintenance` vocabulary, but the Cargo book notes that crates.io no longer uses badges directly.
  https://doc.rust-lang.org/cargo/reference/manifest.html
- RFC 3537 explicitly identifies version maintenance status on crates.io as missing context, especially for users pinned to older but still-supported releases.
  https://rust-lang.github.io/rfcs/3537-msrv-resolver.html
- crates.io policy says ownership transfer requires explicit current-owner approval, making handoff consent a real design problem rather than something heuristics should infer.
  https://crates.io/policies
- `cargo-unmaintained` shows strong demand for lifecycle signals while also demonstrating the limits of activity-based heuristics.
  https://docs.rs/crate/cargo-unmaintained/1.9.0

## Core components

### 1) `lifecycle-intent/v0`
The design-time declaration of a crate’s lifecycle posture.

Required ideas:
- subject identity (crate, workspace member, or version line)
- overall lifecycle status:
  - `active`
  - `passive`
  - `security-fix-only`
  - `frozen`
  - `deprecated`
  - `superseded`
  - `seeking-maintainer`
  - `archived`
- contact / policy references
- effective date and optional expiry / review date
- optional reason codes (`successor-available`, `domain-retired`, `security-risk`, `prototype-only`, `merged-into-workspace`, ...)

Design rule: **lifecycle state is maintainer-declared intent, not an inferred popularity or commit-frequency score**.

### 2) `support-window-map/v0`
Per-version-line support metadata.

Should record:
- semver ranges or named release lines
- support class:
  - `latest-supported`
  - `lts-supported`
  - `security-fix-only`
  - `compatibility-frozen`
  - `unsupported`
- declared MSRV/support constraints when relevant
- support-window start/end dates where known
- notes about backport policy or upgrade expectations

Design rule: **old is not the same as unsupported**.
This artifact exists so Cargo/crates.io/policy tools can say more than “you are not on latest”.

### 3) `successor-map/v0`
Portable successor and replacement metadata.

Should support:
- one or more successor candidates
- replacement class:
  - `drop-in`
  - `migration-required`
  - `conceptual-successor`
  - `org-fork`
  - `temporary-fork`
- verification level:
  - `same-maintainer`
  - `same-org`
  - `registry-verified`
  - `community-asserted`
- reason text / reason codes
- optional migration guide pointers

Design rule: **successor pointers are useful and abusable**.
Verification level must be explicit.

### 4) `handoff-consent/v0`
Explicit maintainer-help or transfer-intent metadata.

Should record:
- whether help is sought (`triage`, `co-maintainer`, `release-manager`, `full-handoff`)
- explicit consent statement
- process or contact URL
- constraints / stewardship expectations
- expiry / supersedes fields

Design rule: **inactivity is not consent**.
This artifact exists precisely because crates.io transfer rules require explicit approval.

### 5) `maintenance-report/v0`
Portable evidence that maintenance happened.

Should record:
- time period and scope
- upkeep classes:
  - triage / issue handling
  - dependency / MSRV maintenance
  - CI / infra repairs
  - security/advisory handling
  - docs or migration upkeep
  - release engineering / compatibility work
- notable outcomes with links
- optional quantified summaries, but never commit-count theater as the only output
- provenance on how the report was generated or curated

Design rule: **maintenance must be legible without being reduced to vanity metrics**.

### 6) `lifecycle-report/v0`
A derived report for a crate, workspace, or lockfile.

Should distinguish signal classes explicitly:
- declared lifecycle metadata
- crates.io metadata
- RustSec lifecycle-relevant advisories
- heuristic findings (`cargo-unmaintained`-style)
- unknown / conflicting status

Should emit reason codes such as:
- `declared-deprecated`
- `successor-present`
- `supported-nonlatest`
- `handoff-requested`
- `rustsec-unmaintained`
- `heuristic-abandonment-suspected`
- `lifecycle-signal-conflict`

Design rule: **declared, security-derived, and heuristic signals must never be flattened into one fake truth**.

### 7) `lifecycle-diff-report/v0`
Structured drift report between two lifecycle states.

Should capture:
- support-window changes
- deprecation or successor changes
- newly requested maintainer help or withdrawn handoff offers
- maintenance-report deltas
- reason-code-level drift (`support-window-narrowed`, `successor-changed`, `maintenance-evidence-added`, ...)

Design rule: lifecycle changes should be reviewable like API or support changes, not rediscovered from release notes months later.

### 8) `lifecycle-pack/v0`
Bundle format containing:
- `lifecycle-intent/v0`
- optional `support-window-map/v0`
- optional `successor-map/v0`
- optional `handoff-consent/v0`
- optional `maintenance-report/v0`
- optional `lifecycle-report/v0`
- optional `lifecycle-diff-report/v0`
- attached raw references when needed

This is the unit that should travel through registry UI, Cargo UX, policy tooling, releases, and later archaeology.

### 9) `cargo lifecycle`
Reference UX:
- `cargo lifecycle init`
- `cargo lifecycle check`
- `cargo lifecycle report`
- `cargo lifecycle diff`
- `cargo lifecycle pack`
- `cargo lifecycle doctor`

`cargo lifecycle` should begin as a metadata + reporting adapter, not as a registry-enforcement system or health-score site.

## Default policy
- **Keep declared intent separate from inferred heuristics.**
- **Support windows are first-class.**
- **Successor verification levels must be explicit.**
- **Handoff requires explicit consent.**
- **Maintenance evidence should reward stewardship work, not just visible feature churn.**

## What the kit should provide to others
- **Trust Signals Kit:** consume lifecycle facts as one dimension of trust rather than owning lifecycle schema itself.
- **Policy Kit:** gate on unsupported, deprecated, or successor-required dependencies without scraping prose.
- **Incident Kit:** attach emergency freezes, deprecations, or successor notes during incidents without conflating them with the incident artifact.
- **Migration Kit:** connect successor pointers and support-window changes to explicit migration plans.
- **Release Pipeline Kit:** attach lifecycle changes to release review.
- **Registry UX / org stewardship:** surface “supported but old”, “looking for maintainer”, and “deprecated with verified successor” cleanly.

## Overlap boundaries
- **Not Trust Signals Kit:** trust aggregates multiple assurance dimensions; lifecycle remains its own source-of-truth layer.
- **Not Incident Kit:** incident workflows handle malicious crates and response operations; lifecycle owns ordinary deprecation/support/succession state.
- **Not Org Identity & Registry UX Kit:** registry/org verification remains separate, though it can verify successor or handoff claims.
- **Not Policy Kit:** policy consumes lifecycle artifacts; it does not define them.
- **Not a maintainer-ranking platform:** the value is portable artifacts and explainable state, not public scoreboards.

## Hard problems (explicitly scoped)
1. **Declared versus inferred truth**
   - v0 must preserve which signals came from maintainers, RustSec, registry metadata, or heuristics.
2. **Version-line nuance**
   - crates often support old lines for compatibility or enterprise reasons; v0 must model that explicitly.
3. **Successor spoofing**
   - successor claims can redirect users; verification level must be first-class.
4. **Maintenance visibility without metric theater**
   - qualitative stewardship work must fit naturally in the model.
5. **Low-friction adoption**
   - maintainers will not fill out giant forms; v0 should allow sparse but meaningful declarations.

## Minimal adoption path
1. Publish schemas and validators for `lifecycle-intent/v0`, `support-window-map/v0`, and `lifecycle-report/v0`.
2. Ship `cargo lifecycle report` that combines declared metadata, RustSec, and heuristic inputs without flattening them.
3. Add `successor-map/v0` and `handoff-consent/v0` for deprecation/help-seeking workflows.
4. Pilot registry and policy consumers.
5. Add `maintenance-report/v0` and diff workflows once teams want visible stewardship evidence.

## Why this is an ecosystem contribution
Rust now has strong security and supply-chain momentum, but its lifecycle language is still primitive.
A good Lifecycle Ledger Kit would supply the missing human-governance substrate beneath trust, policy, migration, and registry UX — without pretending that advisories, activity heuristics, or social media should remain the canonical place to learn whether a crate is supported.
