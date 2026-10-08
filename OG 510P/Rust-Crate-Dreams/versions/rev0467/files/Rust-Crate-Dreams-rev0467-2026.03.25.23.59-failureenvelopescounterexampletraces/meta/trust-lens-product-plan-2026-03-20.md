# Trust Lens — product plan (2026-03-20)

This note sharpens **P-0017 Trust Lens** into an implementation-ready `0.1` shape.

## Main judgment

A worthwhile `0.1` should **not** try to become a universal reputation oracle, a registry moderation replacement, or a magic trust number that other teams are expected to obey.
It should be a **small crate family plus CLI** that helps teams publish one reviewable answer to:

- which dependencies look like identity mistakes or typosquat risks,
- which trust cues came from which plane,
- which assumptions are carrying the posture,
- which dependencies still owe human review,
- and what local policy decision follows from that bundle.

The missing value is the **boring trust-bundle layer** above today’s confusable-name folklore, RustSec advisories, crates.io Security-tab visibility, Trusted Publishing settings, cargo-vet imports, Cargo Scan findings, and research-only trust models.

## What the crate should provide other people

For application teams, crate authors, platform/security teams, and pathfinder/policy tooling, the crate should provide:

1. **One identity-risk report** instead of informal “that name looks suspicious” folklore.
2. **One signal-basis report** instead of collapsing registry, advisory, audit, and inference surfaces together.
3. **One assumption register** instead of hiding the trust model inside a score.
4. **One review-debt report** instead of pretending imported audits erase remaining dangerous-code inspection work.
5. **One policy-decision report** that another team can actually gate on.

## Five first-class review objects

### 1. Identity-risk report

Named classes for `0.1` should focus on identity confusion and impersonation risk such as:

- `no_confusable_signal`
- `name_confusable_detected`
- `campaign_adjacent_identity`
- `owner_or_origin_manual_review_required`
- `manual_review_required`

This object should answer:

- whether a dependency name is confusable with a more established crate,
- whether recent malicious campaigns touched that namespace family,
- whether the risk is simple spelling confusion, broader impersonation pressure, or origin uncertainty,
- and whether the tool is warning about a dependency that should never be auto-approved.

### 2. Signal-basis report

Named classes for `0.1` should focus on trust-plane provenance such as:

- `registry_signal`
- `advisory_signal`
- `publishing_identity_signal`
- `audit_import_signal`
- `effect_scan_signal`
- `research_model_signal`
- `manual_declaration`
- `inference`

This object should answer:

- which cues came from crates.io,
- which came from RustSec,
- which came from cargo-vet or shared audit files,
- which came from Cargo Scan / similar effect analysis,
- which came from Cargo Sherlock-style assumption models,
- and which claims are inferred locally rather than imported from an authority.

### 3. Assumption register

Named classes for `0.1` should focus on explicit trust assumptions such as:

- `no_known_advisory_at_capture_time`
- `trusted_publishing_enabled`
- `audit_importer_trusted`
- `effect_scan_context_review_pending`
- `download_or_popularity_signal_weak_only`
- `manual_review_required`

This object should answer:

- what must remain true for the current posture to stay acceptable,
- which assumptions are weak tie-breaks versus hard gates,
- which assumptions are imported from external tools,
- and which assumptions should force review rather than silent approval.

### 4. Review-debt report

Named classes for `0.1` should focus on unresolved human work such as:

- `no_open_review_debt`
- `dangerous_effect_review_pending`
- `context_sensitive_audit_pending`
- `identity_review_pending`
- `policy_exception_pending`
- `manual_review_required`

This object should answer:

- whether dangerous-code or effect-analysis review remains,
- whether cargo-vet gaps or exceptions still exist,
- whether confusable identity review remains unresolved,
- and whether the graph is only “acceptable” because debt is explicitly deferred.

### 5. Policy-decision report

Named classes for `0.1` should focus on conservative operational posture such as:

- `allow`
- `warn`
- `manual_review_required`
- `deny`

This object should answer:

- what the current local decision is,
- which reports caused it,
- which dependencies were decisive,
- and whether the result is stable enough for CI gating or only fit for review.

## Recommended `0.1` command surface

### `cargo trust-lens capture`
Capture graph structure plus imported trust signals and emit:
- `identity-risk.report.json`
- `signal-basis.report.json`
- `assumption-register.report.json`
- `review-debt.report.json`

### `cargo trust-lens check`
Run conservative local policy checks and emit:
- `policy-decision.report.json`

### `cargo trust-lens explain`
Render a human-readable summary of the decisive identity, signal, assumption, and debt findings.

### `cargo trust-lens diff`
Compare two trust bundles across dependency updates or policy changes.

### `cargo trust-lens bundle`
Produce one compact `.trustlensbundle.zip` containing reports, notes, and selected imports.

## Recommended crate/workspace split

- `trust_lens_model`
- `trust_lens_identity`
- `trust_lens_import_registry`
- `trust_lens_import_audit`
- `trust_lens_policy`
- `cargo-trust-lens`

## `0.1` artifact set

Core artifacts should be:
- `trust-policy.toml`
- `identity-risk.report.json`
- `signal-basis.report.json`
- `assumption-register.report.json`
- `review-debt.report.json`
- `policy-decision.report.json`
- `trust-notes.summary.md`

## Discovery order

1. **Import graph and registry facts**
   - resolved dependency graph
   - crates.io Security-tab visibility
   - Trusted Publishing posture when available
   - publish timing / version freshness when relevant
2. **Import advisory facts**
   - RustSec advisories
   - malicious-crate removals
   - yanks and other high-signal warning states when available
3. **Import audit/review substrate**
   - cargo-vet audits and exemptions
   - Cargo Scan or similar effect-analysis outputs when present
   - Cargo Sherlock-style assumption models when present
4. **Normalize identity risk**
   - confusable names
   - campaign-adjacent names
   - owner/origin uncertainty
5. **Normalize review debt**
   - dangerous effects pending review
   - context-sensitive call-graph review pending
   - identity review pending
6. **Decide policy posture**
   - allow / warn / manual_review_required / deny

## Ranking discipline

A good `0.1` should not let “score” become the contract.
It should keep separate:

- `identity_risk_known`
- `advisory_state_known`
- `publishing_identity_known`
- `audit_import_known`
- `review_debt_known`
- `manual_review_required`

An optional numeric trust-cost may exist, but only as **one derived view** over explicit assumptions and signals.

## What to import from substrate, and what not to flatten

### Import, but do not flatten
- crates.io Security-tab visibility
- Trusted Publishing posture
- RustSec advisories and malicious-crate removals
- cargo-vet audits / exemptions
- Cargo Scan findings where available
- Cargo Sherlock assumption models where available
- simple identity/confusable analysis over the resolved graph

### Do not flatten into one fake verdict
- “there is no advisory visible right now”
- “the crate uses trusted publishing”
- “another team audited some versions”
- “the trust-cost number is low”
- “the name only differs by a character or two”

## Preferred proving grounds

- a dependency graph containing a confusable crate name adjacent to a recent malware campaign
- a graph with clean RustSec/security-tab posture but unresolved dangerous-effect review debt
- a graph that imports cargo-vet audits but still has identity-review or context-sensitive audit gaps
- a graph where popularity and recent publish activity would look reassuring without actually answering trust posture

## Non-goals

- not a global reputation board
- not a crates.io moderation tool
- not a universal proof of safety
- not a replacement for cargo-vet, cargo-audit, Cargo Scan, or Cargo Sherlock
- not a popularity leaderboard with security branding

## MVP API sketch

```rust
pub fn capture_identity_risk(input: &TrustInput) -> Result<IdentityRiskReport>;
pub fn capture_signal_basis(input: &TrustInput) -> Result<SignalBasisReport>;
pub fn capture_assumption_register(input: &TrustInput) -> Result<AssumptionRegisterReport>;
pub fn capture_review_debt(input: &TrustInput) -> Result<ReviewDebtReport>;
pub fn check_policy(bundle: &TrustBundle, policy: &TrustPolicy) -> Result<PolicyDecisionReport>;
pub fn write_bundle(bundle: &TrustBundle, out: &Path) -> Result<()>;
```

## Maintenance posture

- Preserve `manual_review_required` as an honest output.
- Keep registry/advisory/imported-audit signals distinct from local inference.
- Compose with pathfinder, crate health, and off-ramp lanes instead of blurring into them.
- Prefer explainable assumptions over clever opaque scoring.

## Sources

- https://blog.rust-lang.org/2026/01/21/crates-io-development-update/
- https://blog.rust-lang.org/2026/02/13/crates.io-malicious-crate-update/
- https://rustsec.org/advisories/RUSTSEC-2026-0027
- https://rustsec.org/advisories/RUSTSEC-2026-0039
- https://mozilla.github.io/cargo-vet/
- https://arxiv.org/abs/2512.12553
- https://arxiv.org/abs/2602.06466
