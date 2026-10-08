# Pathfinder evidence-gap campaign plan — 2026-03-24

## Why this lane matters now

The archive’s front-door stack now has strong answers for:
- comparing candidates,
- freezing a basis,
- importing review packets,
- adjudicating disagreement,
- recording bounded exceptions,
- reopening review later,
- profiling for different adopters,
- and running staged adoption programs.

What it still lacked was a compact answer to the next practical question teams ask:

> “What is the smallest bounded plan for closing the missing proof that blocks the next stage?”

The current Rust ecosystem now has enough official substrate to justify a real product answer:

- Cargo plumbing work explicitly decomposes Cargo into programmatic phases;
- Cargo build-analysis is explicitly about recording build metadata across invocations for later explanation;
- docs.rs exposes hosted build posture, custom metadata, rustdoc JSON, download archives, and public queue state;
- crates.io exposes Security-tab data, Trusted Publishing posture, and `pubtime`;
- Cargo Vet already models backlog, suggestions, exemptions, imported audits, trusted publishers, and expiring renewals;
- cargo-deny already models feature and workspace scope from Cargo graph construction and exposes shared options for feature activation/workspace roots.

That is enough to justify a bounded **gap-campaign** layer above the existing packet family.

## Product concept

`P-0509 Crate Ecosystem Pathfinder & Decision-Pack Kit` should gain a new receiver-facing layer:

- `evidence-gap.report.json`
- `evidence-campaign.plan.json`
- `gap-closure.receipt.json`

These artifacts do **not** replace:
- `decision-pack.report.json`,
- `candidate-basis.receipt.json`,
- `policy-profile.pack.json`,
- `profile-satisfaction.report.json`,
- `adjudication-session.report.json`,
- `policy-exception.receipt.json`,
- or `profile-progression.report.json`.

They sit **above** them and answer:
- which exact gate is still unsatisfied,
- which evidence route could close it,
- what automation class is appropriate,
- what remains blocked or manual,
- and what changed when one gap was actually closed.

## What the crate should provide other people

### 1. Explicit gap extraction

The crate should derive a compact `evidence-gap.report` from existing packets.

For each gap, it should record:
- a stable `gap_id`,
- the failed gate or stage condition,
- the gap class,
- the current severity,
- which existing packet exposed it,
- and whether the gap looks automatable, manual-artifact, manual-judgment, or blocked-upstream.

### 2. Authority-route mapping

The crate should say **where** a gap can be worked.

Examples:
- `cargo metadata --format-version ...`
- Cargo build-analysis import
- docs.rs build metadata / rustdoc JSON / download archive import
- crates.io Security / Trusted Publishing / `pubtime` import
- Cargo Vet suggest / inspect / diff / certify / renew
- cargo-deny target/feature/workspace scoped graph run

It should not collapse those into one generic “evidence collected” story.

### 3. One bounded campaign plan

The crate should emit one small `evidence-campaign.plan` saying:
- which gaps are in scope,
- which artifact each action intends to produce,
- who owns the action,
- whether it is local-command, hosted-import, manual-review, or upstream-request,
- and what counts as success, partial success, or blocked.

### 4. Gap-closure receipts

When a gap changes state, the crate should emit a `gap-closure.receipt` saying:
- which gap moved,
- which artifacts were produced,
- whether the gap is closed, partially closed, blocked, reopened, or still manual-review-required,
- and which earlier basis remains inherited.

### 5. Campaign stop conditions

A worthy crate should make it easy to stop.

Examples:
- `stage_can_progress`
- `gap_moved_to_exception`
- `blocked_upstream`
- `requires_manual_adjudication`
- `new_compare_required`

### 6. Refusal boundaries

The crate must refuse to claim:
- that a campaign plan is a workflow platform,
- that importing more public metadata always closes a task-fit gap,
- that docs.rs download archives are ready-made offline docs,
- that a Security-tab entry decides task fit,
- that Trusted Publishing decides task fit,
- or that an automatable gap means the stage can definitely progress.

## CLI sketch

- `cargo pathfinder gaps derive --from <bundle-dir>`
- `cargo pathfinder gaps explain <gap-id>`
- `cargo pathfinder campaign init --from evidence-gap.report.json`
- `cargo pathfinder campaign run --plan evidence-campaign.plan.json --dry-run`
- `cargo pathfinder campaign close --gap <gap-id> --artifact <path>`
- `cargo pathfinder campaign summarize --from <packet-dir>`

## Library sketch

```rust
pub struct EvidenceGapReport {
    pub report_id: String,
    pub stage_id: String,
    pub subject_ref: String,
    pub open_gaps: Vec<EvidenceGap>,
}

pub struct EvidenceCampaignPlan {
    pub plan_id: String,
    pub report_ref: String,
    pub campaign_items: Vec<CampaignItem>,
    pub stop_conditions: Vec<StopCondition>,
}

pub struct GapClosureReceipt {
    pub receipt_id: String,
    pub plan_ref: String,
    pub gap_id: String,
    pub status: GapClosureStatus,
    pub produced_artifacts: Vec<String>,
}

pub fn derive_gaps(bundle: &PathfinderBundle) -> EvidenceGapReport;
pub fn plan_campaign(report: &EvidenceGapReport) -> EvidenceCampaignPlan;
pub fn close_gap(
    plan: &EvidenceCampaignPlan,
    gap_id: &str,
    new_artifacts: &[String],
) -> GapClosureReceipt;
```

## `0.1` release boundary

A believable `0.1` should support:
- one gap-report vocabulary,
- one campaign-plan vocabulary,
- one closure-receipt vocabulary,
- four automation classes,
- and one small stop-condition set.

It does **not** need:
- cross-team ticket sync,
- regulator-specific workflow ownership,
- generalized task orchestration,
- or automatic signoff in external systems.

## Scenario pack for first implementation

### `enterprise_offline_stage_turns_open_gaps_into_campaign_without_rewriting_basis`

Proves that:
- a previously frozen basis can remain intact,
- an enterprise-offline stage can surface concrete missing evidence,
- those missing items can become a bounded campaign plan,
- and one closure receipt can advance only one gap without pretending the stage is fully done.

## Ranking consequence

This plan does **not** promote a new top-lane proposal.
It strengthens the practical definition of the existing front door.

A worthy front-door crate now needs to hand other people not only a comparison and a profile answer,
but also a **small plan for closing what is still missing** without lying about what remains manual.

## Sources

- Rust challenges
- 2025 State of Rust survey results
- Rust in 2026 / flagships
- Prototype a new set of Cargo plumbing commands
- Prototype Cargo build analysis
- docs.rs builds / metadata / rustdoc JSON / download / queue
- crates.io development update
- Cargo Vet config / commands / wildcard audits
- cargo-deny common options
