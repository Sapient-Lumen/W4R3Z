# Pathfinder decision-program runbook plan — 2026-03-24

## Why this lane matters now

The archive’s front-door stack now has strong answers for:
- comparing candidates,
- freezing a basis,
- importing/receiving review packets,
- adjudicating disagreement,
- recording bounded exceptions,
- reopening review later,
- and answering honestly for different adopter profiles.

What it still lacked was a compact answer to the next question teams ask in practice:

> “How do we move from prototype confidence to operational confidence without starting over or pretending yesterday’s packet already answered tomorrow’s question?”

The current Rust ecosystem now has enough official substrate to justify a real product answer:
- Cargo decomposes work into phases in the cargo-plumbing goal;
- Cargo build-analysis is explicitly about persisting machine-readable build data across invocations;
- docs.rs exposes hosted build posture, custom metadata, versioned rustdoc JSON, and offline-download caveats;
- crates.io exposes timing/trust signals like `pubtime`, Security tab, and Trusted Publishing;
- Cargo Vet exposes policies, criteria, imports, exemptions, and expiring renewals;
- cargo-deny exposes target-scoped graphs and offline caveats;
- and safety-critical guidance explicitly describes staged narrowing, wrapping, and replace-later dependency programs.

That is enough to justify a **decision-program runbook** above the existing packet family.

## Product concept

`P-0509 Crate Ecosystem Pathfinder & Decision-Pack Kit` should gain a new receiver-facing layer:

- `decision-program.runbook.json`
- `profile-progression.report.json`
- later: `program-exit.report.json`

These artifacts do **not** replace:
- `task-profile.json`,
- `decision-pack.report.json`,
- `candidate-basis.receipt.json`,
- `policy-profile.pack.json`,
- `profile-satisfaction.report.json`,
- `adjudication-session.report.json`,
- or `policy-exception.receipt.json`.

They sit **above** them and answer:
- which staged adoption program is being run,
- which stage is active now,
- what evidence gates must be passed before progressing,
- what can be carried forward,
- and which exit posture the team reached.

## What the crate should provide other people

### 1. Stable named stages

Examples for `0.1`:
- `explore`
- `team_default`
- `enterprise_offline_gate`
- `safety_onramp_gate`

Each stage should state:
- intended receivers,
- required input artifacts,
- approval roles,
- allowed exit statuses,
- and explicit reopen triggers.

### 2. Stage-entry evaluation

The crate should evaluate whether a candidate or frozen starter set has enough evidence to enter or leave a stage, such as:
- basis lock present,
- knowledge pack present,
- profile-satisfaction report present,
- open exception count within budget,
- target/support truth present,
- source-parity evidence present where required,
- docs.rs parity or hosted build notes imported,
- build-analysis or lifecycle notes imported where required.

### 3. Program runbook

The crate should emit one compact artifact saying:
- what the stages are,
- which packet families each stage consumes and emits,
- who signs off or reviews,
- what “progress”, “hold”, “split boundary”, and “replace later” mean,
- and which triggers reopen a stage instead of reopening the whole world.

### 4. Profile progression report

A later step should answer:
- what exactly was inherited from the earlier stage,
- what new evidence was added,
- what stayed unresolved,
- which exceptions remain active,
- and what the current stage exit status is.

### 5. Tool-local mapping, shared program language

The crate should map tool-local surfaces into a shared program language without pretending the tools mean the same thing.

Examples:
- Cargo Vet criteria / exemptions / renewals,
- cargo-deny offline posture / ignored advisories / target filters,
- docs.rs metadata/build posture,
- crates.io Trusted Publishing / `pubtime`,
- Cargo metadata and basis locks,
- build-analysis timing / rebuild reasons / invocation metadata,
- and source-parity or lifecycle packets from adjacent crates.

### 6. Refusal boundaries

The crate must refuse to claim:
- that stage progression equals certification,
- that a later stage retroactively changes the old basis,
- that hosted docs visibility means enterprise-offline readiness,
- that a single unexpired exception proves the gate is satisfied,
- or that “good enough for team default” implies “good enough for safety-onramp”.

## CLI sketch

- `cargo pathfinder program list`
- `cargo pathfinder program show enterprise-offline-gate`
- `cargo pathfinder program init --task service_with_background_jobs`
- `cargo pathfinder program assess --stage team_default`
- `cargo pathfinder program progress --from explore --to enterprise_offline_gate`
- `cargo pathfinder program exit --status split_boundary`

## Library sketch

```rust
pub struct DecisionProgramRunbook {
    pub program_id: String,
    pub program_version: String,
    pub stages: Vec<ProgramStage>,
    pub progression_rules: Vec<ProgressionRule>,
    pub reopen_triggers: Vec<ReopenTrigger>,
}

pub struct ProfileProgressionReport {
    pub report_id: String,
    pub from_stage: String,
    pub to_stage: String,
    pub inherited_artifacts: Vec<String>,
    pub newly_required_artifacts: Vec<String>,
    pub unresolved_gaps: Vec<String>,
    pub exit_status: ProgramExitStatus,
}

pub fn assess_progression(
    runbook: &DecisionProgramRunbook,
    prior_bundle: &PathfinderBundle,
    next_stage: &str,
) -> ProfileProgressionReport;
```

## `0.1` release boundary

A believable `0.1` should support:
- one staged program family,
- four built-in stages,
- two outputs (`decision-program.runbook`, `profile-progression.report`),
- one narrow program-exit vocabulary,
- and carry-forward of prior basis, exceptions, and profile-satisfaction reports.

It does **not** need:
- every regulated-domain program,
- automatic policy import from every third-party tool,
- automated signoff workflows in external ticketing systems,
- or a stable policy language beyond the small JSON packet surface.

## Scenario pack for first implementation

### `explore_packet_graduates_to_enterprise_offline_without_rewriting_basis`

Proves that:
- one starter set can begin in an exploratory program stage,
- a later enterprise-offline stage can reuse the old basis lock rather than pretending it never existed,
- new artifacts can be added without rewriting the historical packet,
- and the stage can still stop at `conditional_keep` when mirror/source-parity gaps remain.

## Ranking consequence

This plan does **not** promote a new top-lane proposal.
It strengthens the practical definition of the existing front door.

A worthy front-door crate now needs to hand other people not only a comparison and a profile answer,
but a comparison and profile answer that can survive **programmed progression** without lying.

## Sources

- Rust challenges
- 2025 State of Rust survey results
- Rust in 2026 / flagships
- Prototype a new set of Cargo plumbing commands
- Prototype Cargo build analysis
- docs.rs builds / metadata / rustdoc JSON / download
- crates.io development update
- Cargo Vet config / criteria / commands
- cargo-deny config / offline behavior
- safety-critical Rust
