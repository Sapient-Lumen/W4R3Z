# V0 kernel brief: Package Intake Review Kit

## Identity
- candidate: **Package Intake + Release Boundary Review**
- macro-program: **Package Intake + Release Boundary Review**
- current verdict context: `advance`
- kernel codename: `intake-review-kit/v0`

## Why this kernel and not a bigger build
The first honest build is not a universal trust oracle and not a registry-global policy engine.
It is a **local-first intake review kit** for release and dependency-boundary decisions.
That is justified because the ecosystem now has more concrete provenance and security signals — Trusted Publishing expansion, provider-specific caveats, capability-analysis prototypes, vulnerability-surfacing work, provenance tracking, and recent extraction-path incident posture — but operator and route differences remain real.
Relevant sources:
- https://blog.rust-lang.org/2026/01/21/crates-io-development-update/
- https://blog.rust-lang.org/inside-rust/2026/02/09/project-director-update/
- https://rustfoundation.org/media/strengthening-rust-security-with-alpha-omega-a-progress-update/
- https://blog.rust-lang.org/2026/03/21/cve-2026-33056/

## Repo shape
Suggested first repo tree:
- `policies/route-profiles/` — review profiles for GitHub Trusted Publishing, GitLab.com Trusted Publishing, token publishing, alternate registries
- `receipts/intake/` — review receipts for a release or dependency intake decision
- `receipts/waivers/` — explicit waiver records with expiry and owner
- `receipts/quarantine/` — quarantine or escalation records
- `drills/incident-replays/` — replay cases for known incident classes
- `crates/intake-cli/` — optional command-line validator and receipt generator
- `schemas/intake-receipt-v0.schema.json`
- `docs/operator-guidance.md`

## User surfaces
The first user surfaces should be:
1. `review` — create a bounded intake receipt from local project inputs
2. `waive` — record a risk acceptance with owner and expiry
3. `quarantine` — mark a dependency or publish route for extra review
4. `drill` — replay a recent incident class against the current policy profile

The first receipt should answer:
- what route is being used to publish or intake
- whether Trusted Publishing or tokens are involved
- registry scope and alternate-registry caveats
- what local evidence was reviewed
- what was accepted, waived, blocked, or escalated

## Import seams
Required imports should be local and explicit:
- manifest / lockfile / dependency graph data
- release-workflow metadata
- current advisory feeds or vulnerability signals
- route-profile configuration

Optional imports:
- capability-analysis output in a Capslock-compatible form when available
- provenance-tracking or signed-metadata receipts when the route supports them

Do not require a central service for first use.

## Proof assets
The kernel should emit:
- one intake receipt per decision
- one waiver or escalation receipt when applicable
- one route-profile snapshot
- one incident-replay result showing how the current policy would behave

## Proving grounds
Start with:
1. one crates.io publish flow using Trusted Publishing
2. one crates.io publish flow that still uses tokens
3. one alternate-registry path with explicit uncertainty/caveats
4. one dependency-intake review against a known recent incident class

## Owner shape / upkeep
Best first owner:
- security-adjacent operator team or release-engineering group

Immediate upkeep tax:
- route-profile drift
- advisory-feed and incident-drill refresh
- waiver expiry enforcement
- registry-specific differences

## Refused expansions
Do not let v0 become:
- a global trust score
- a mandatory gate for all Rust package use
- a central service that replaces local operator judgment
- or a false claim that crates.io behavior automatically generalizes to alternate registries

## Exit criteria
This kernel has earned a stronger next stage when it can show:
- successful use across multiple route profiles
- repeatable incident drills with explicit local decisions
- clear waiver / quarantine / escalation histories
- and optional capability/provenance imports that improve decisions without becoming mandatory theater

