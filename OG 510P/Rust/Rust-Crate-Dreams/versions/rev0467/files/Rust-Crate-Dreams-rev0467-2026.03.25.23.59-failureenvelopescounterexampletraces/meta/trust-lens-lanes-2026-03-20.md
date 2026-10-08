# Trust-lens lane boundaries (2026-03-20)

This note exists so the archive does not flatten several adjacent ecosystem/security lanes into one fake “trust score” crate.

## Core judgment

**P-0017 Trust Lens** should be the lane for:

- dependency-graph **identity-risk truth**,
- **signal-basis / trust-plane provenance**,
- explicit **assumption registers**,
- explicit **review debt**,
- and conservative **policy-decision posture**.

It is the lane for the question:

> “What trust assumptions and unresolved risks is this team being asked to accept when they carry this dependency graph?”

## Keep separate from these adjacent lanes

### 1. P-0509 Crate Ecosystem Pathfinder & Decision-Pack Kit

Pathfinder is about **task fit, starter-set choice, freezeability, and decision aging**.

Trust Lens is **not**:
- a general crate recommender,
- a task-first ranking engine,
- a teaching/production starter-set chooser,
- or a frozen-decision watch engine.

Pathfinder may **import** trust artifacts.
It does not own them.

### 2. P-0011 Crate Health Contract Kit

Crate Health is about **support windows, succession posture, and maintainer intent**.

Trust Lens is **not**:
- a support-horizon contract,
- a bus-factor declaration,
- or a maintainer-responsiveness model.

Trust signals can inform health review.
Health artifacts can inform trust review.
They are not the same lane.

### 3. cargo-vet / audit-sharing substrate

`cargo vet` is about **matching dependencies against audits performed by trusted entities** and ratcheting audit debt down over time.

Trust Lens is **not**:
- an audit-sharing protocol,
- a replacement for audits.toml,
- or an implementation of relative audits.

Trust Lens may import audit signals and exceptions.
It should not replace the substrate.

### 4. Cargo Scan / effect-analysis substrate

Cargo Scan is about **identifying potentially dangerous effects** and shrinking what humans need to inspect.

Trust Lens is **not**:
- a whole-program effect-analysis tool,
- a dangerous-code classifier,
- or a call-graph workbench.

Trust Lens may import effect-analysis outcomes as **review debt**.
It should not absorb the underlying analysis lane.

### 5. Crates.io moderation / registry policy

Registry policy is about:
- crate takedowns,
- moderation,
- anti-abuse controls,
- and official publication rules.

Trust Lens is **not**:
- a registry-enforcement engine,
- a name-registration policy proposal,
- or a takedown workflow.

It consumes registry/advisory facts; it does not govern the registry.

### 6. P-0515 Crate Off-Ramp Pack Kit

Off-ramp is about **leaving** a crate safely: successor maps, checked exit recipes, and sunset posture.

Trust Lens is **not**:
- the migration recipe,
- the successor chooser,
- or the compatibility witness for leaving.

A trust result may say “deny” or “manual review required.”
Off-ramp owns the actual leaving workflow.

## Allowed imports

Trust Lens may import:
- crates.io Security-tab visibility,
- Trusted Publishing posture,
- RustSec advisories,
- cargo-vet audits and exemptions,
- Cargo Scan findings,
- Cargo Sherlock outputs,
- and local policy files.

But it must keep visibly separate:
- `registry_signal`
- `advisory_signal`
- `audit_import_signal`
- `effect_scan_signal`
- `research_model_signal`
- `inference`
- `manual_review_required`

## Preferred proving grounds

The best tests for this lane are not “largest crate on crates.io.”
They are cases like:

- confusable or campaign-adjacent dependency names,
- clean registry surfaces with unresolved review debt,
- imported audits that still leave identity or context-sensitive trust questions,
- and graphs where a weak numeric score would tempt people to over-trust the result.

## Failure mode to resist

Do not let future passes quietly rephrase this lane as:
- “better security scoring,”
- “a crates.io policy engine,”
- “a cargo-vet replacement,”
- or “a dashboard of every possible trust signal.”

The archive now has a distinct lane for the **reviewable dependency trust bundle**.
