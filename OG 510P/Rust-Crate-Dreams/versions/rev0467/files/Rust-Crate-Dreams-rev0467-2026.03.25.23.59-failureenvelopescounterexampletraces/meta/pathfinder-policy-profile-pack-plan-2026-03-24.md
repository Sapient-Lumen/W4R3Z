# Pathfinder policy profile pack plan — 2026-03-24

## Why this lane matters now

The archive’s front-door stack now has strong answers for:
- comparing candidates,
- freezing a basis,
- importing/receiving review packets,
- adjudicating disagreement,
- recording bounded exceptions,
- and reopening review later.

What it still lacks is a compact answer to the next question teams ask in practice:

> “Which version of this packet should *we* believe, given our deployment posture, audit appetite, offline needs, and assurance expectations?”

The Rust ecosystem now has enough official substrate to justify a real product answer:
- Cargo exposes versioned machine-readable metadata;
- docs.rs exposes versioned rustdoc JSON and visible hosted-build posture;
- crates.io exposes publication timing and publishing-trust surfaces;
- Cargo Vet exposes custom criteria and subtree policy;
- cargo-deny exposes target-scoped policy and exception structure;
- and safety-critical guidance explicitly calls for reusable playbooks, MSRV conventions, and target-readiness checklists.

That is enough to justify a **policy-profile pack** above the existing packet family.

## Product concept

`P-0509 Crate Ecosystem Pathfinder & Decision-Pack Kit` should gain a new receiver-facing layer:

- `policy-profile.pack.json`
- `profile-satisfaction.report.json`
- later: `profile-diff.report.json`

These artifacts do **not** replace:
- `task-profile.json`,
- `decision-pack.report.json`,
- `candidate-basis.receipt.json`,
- `adjudication-session.report.json`,
- or `policy-exception.receipt.json`.

They sit **above** them and answer:

- which adopter profile is asking,
- which evidence floors apply,
- which missing surfaces block a clean answer,
- and whether the outcome is pass / conditional / fail / manual-review-required for that profile.

## What the crate should provide other people

### 1. Stable named profiles

Examples for `0.1`:
- `explore-default`
- `team-default`
- `enterprise-offline`
- `safety-onramp`

Each profile should state:
- intended user/receiver,
- required evidence floors,
- allowed exceptions budget,
- escalation rules,
- and explicit non-claims.

### 2. Evidence-floor evaluation

The crate should evaluate whether a candidate or frozen starter set satisfies profile requirements such as:

- pinned basis lock present,
- knowledge pack present,
- docs visibility present,
- registry release timing captured,
- publishing/trust posture captured,
- target-support truth present,
- MSRV or toolchain floor explicit,
- source-parity evidence required or optional,
- audit-policy evidence required or optional,
- manual-review ceiling still present.

### 3. Profile satisfaction report

The crate should emit one compact artifact saying:
- which floors were satisfied,
- which are missing,
- which are conditional,
- which exceptions are currently spending the profile’s budget,
- and what next action is needed.

### 4. Profile diff

A later step should answer:
- what changed moving from `explore-default` to `enterprise-offline`,
- what changed moving from `team-default` to `safety-onramp`,
- and which evidence artifacts can be reused versus which must be regenerated.

### 5. Tool-local mapping, shared packet language

The crate should map tool-local surfaces into a shared packet language without pretending the tools mean the same thing.

Examples:
- Cargo Vet criteria / exemptions / trust entries,
- cargo-deny ignored advisories / license exceptions / bans,
- docs.rs metadata/build posture,
- crates.io Trusted Publishing / `pubtime`,
- registry-index facts,
- Cargo metadata and basis locks.

### 6. Refusal boundaries

The crate must refuse to claim:
- that a profile equals certification,
- that Trusted Publishing or a Security tab means task fit,
- that hosted docs visibility means offline or target support truth,
- that an exploratory profile implies production approval,
- or that a safety-onramp profile proves standards compliance.

## CLI sketch

- `cargo pathfinder profile list`
- `cargo pathfinder profile show safety-onramp`
- `cargo pathfinder assess --profile enterprise-offline`
- `cargo pathfinder assess --profile safety-onramp --frozen-basis pathfinder-bundle.json`
- `cargo pathfinder diff-profile explore-default safety-onramp`
- `cargo pathfinder emit profile-pack --profile team-default`

## Library sketch

```rust
pub struct PolicyProfilePack {
    pub profile_id: String,
    pub profile_kind: ProfileKind,
    pub version: String,
    pub required_floors: Vec<EvidenceFloor>,
    pub allowed_exception_budget: ExceptionBudget,
    pub non_claims: Vec<NonClaim>,
}

pub struct ProfileSatisfactionReport {
    pub profile_id: String,
    pub task_id: String,
    pub subject: SubjectRef,
    pub status: SatisfactionStatus,
    pub satisfied: Vec<SatisfiedFloor>,
    pub missing_or_manual: Vec<UnsatisfiedFloor>,
    pub exception_budget: ExceptionBudgetStatus,
    pub next_actions: Vec<NextAction>,
}

pub fn evaluate_profile(
    profile: &PolicyProfilePack,
    bundle: &PathfinderBundle,
) -> ProfileSatisfactionReport;
```

## `0.1` release boundary

A believable `0.1` should support:
- one frozen starter set or candidate comparison,
- four built-in profiles,
- two outputs (`policy-profile.pack`, `profile-satisfaction.report`),
- and one profile-difference explanation in human-readable notes.

It does **not** need:
- automatic certification exports,
- every domain-specific profile,
- policy import from every third-party tool,
- or a stable policy DSL beyond the small JSON packet surface.

## Scenario pack for first implementation

### `same_task_under_explore_enterprise_and_safety_profiles_yields_different_gates`

Proves that:
- one async/web/service-oriented starter set may be acceptable for exploratory work,
- the same set may become conditional for enterprise-offline due to source-parity and mirror gaps,
- and the same set may remain manual-review-required for safety-onramp until target, MSRV, and lifecycle evidence are strengthened.

## Ranking consequence

This plan does **not** promote a new top-lane proposal.
It strengthens the practical definition of the existing front door.

A worthy front-door crate now needs to hand other people not only a comparison,
but a comparison that can survive different adopter profiles without lying.

## Sources

- Rust challenges
- 2025 State of Rust survey results
- Rust in 2026 / flagships
- safety-critical Rust
- cargo metadata
- docs.rs rustdoc JSON
- crates.io development update
- Cargo Vet config / criteria / how it works
- cargo-deny advisory / bans / licenses config
