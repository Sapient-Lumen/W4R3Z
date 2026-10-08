# Crate health lane boundaries (2026-03-20)

This note exists so the archive does not flatten several adjacent ecosystem lanes into one fake “maintenance status” crate.

## Core judgment

**P-0011 Crate Health Contract Kit** should be the lane for:

- maintainer-authored **maintenance-window truth**,
- **succession / backup / handoff** posture,
- declared **support intent** (MSRV, issue/security response expectations, support horizon),
- and conservative **health-check consistency** between declared posture and visible registry/repo signals.

It is the lane for the question:

> “What support and stewardship promise is this crate actually making to downstream users?”

## Keep separate from these adjacent lanes

### 1. P-0509 Crate Ecosystem Pathfinder & Decision-Pack Kit

Pathfinder is about **task fit, role coverage, evidence origin, freshness, and starter-set choice**.

Crate Health is **not**:
- a ranking algorithm,
- a recommendation engine,
- a search-result reorderer,
- or a “best crate” verdict.

Pathfinder may **import** health artifacts.
It does not own them.

### 2. P-0515 Crate Off-Ramp Pack Kit

Off-ramp is about **how to leave** a crate: successors, stopgaps, checked exit recipes, sunset diffs.

Crate Health is **not**:
- the exit plan itself,
- a migration recipe,
- or a successor compatibility witness.

Health may say a crate is seeking handoff or entering sunset.
Off-ramp owns the **receiver-facing leaving-the-crate workflow**.

### 3. P-0017 Trust Lens / supply-chain trust lanes

Trust lenses are about **provenance, publication identity, verified mirrors, signatures, advisories, and security posture**.

Crate Health is **not**:
- a supply-chain score,
- a signature verifier,
- a RustSec dashboard,
- or a trusted-publishing policy engine.

Health may import trust signals, but must not pretend:
- “trusted publishing enabled” means “actively maintained”,
- or “no advisory shown” means “support commitment exists”.

### 4. P-0483 Public API Readiness Bundle Kit

Public API readiness is about **release-review truth** for a specific release transition.

Crate Health is **not**:
- a semver verdict,
- a docs-readiness gate,
- or a public-surface diff.

A crate may be healthy and still ship a poor release.
A crate may ship a careful release and still have weak succession posture.

### 5. Generic repository analytics / vanity dashboards

Crate Health should not collapse into:
- stars/downloads/activity graphs,
- “bus factor” theatre without maintainer declarations,
- or a hosted social leaderboard.

Those may inform a review.
They are not the contract.

## Allowed imports

Crate Health may import:
- crates.io Security-tab visibility,
- trusted-publishing posture,
- release quietness or cadence facts,
- maintainer/owner counts,
- mutable registry metadata when it exists,
- and maintainer-authored support documents.

But it must keep visibly separate:
- `imported_signal`
- `maintainer_declared`
- `inferred`
- `manual_review_required`

## Preferred proving grounds

The best tests for this lane are not “top crate on crates.io.”
They are cases like:

- quiet but honestly reactive crates,
- one-person-maintained crates with or without a declared backup,
- sunset-in-progress crates with unclear support windows,
- and crates whose trust/security signals are stronger than their support clarity.

## Failure mode to resist

Do not let future passes quietly rephrase this lane as:
- “better ranking”,
- “better trust scoring”,
- “better deprecation metadata”,
- or “better repository analytics”.

The archive now has a distinct lane for the **maintainer-facing health/support/succession contract**.
