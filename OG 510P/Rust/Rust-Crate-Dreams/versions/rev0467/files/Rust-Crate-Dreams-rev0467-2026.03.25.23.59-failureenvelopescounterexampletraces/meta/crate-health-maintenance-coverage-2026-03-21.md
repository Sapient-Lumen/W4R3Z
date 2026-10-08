# Crate health maintenance-coverage boundaries — 2026-03-21

This note keeps **P-0011 Crate Health Contract Kit** from collapsing support posture into fake uniform maintenance coverage.

## The sharper seam

Within **P-0011**, keep these truths separate:

1. **broad health profile exists**,
2. **maintenance window exists**,
3. **succession / backup posture exists**,
4. **support intent exists**,
5. **specific maintenance work classes are actually covered**,
6. **important duty classes are only best-effort, inferred, or still unowned**.

Those are related, but they are not the same stewardship claim.

## What belongs in the maintenance-coverage seam

The maintenance-coverage seam is about questions like:

- Which keep-the-lights-on duties are explicitly covered?
- Which contributor-enabling duties are explicitly covered?
- Which duties have a named owner, backup, or only a vague best-effort promise?
- Does current health language hide that CI breakage, security response, docs upkeep, or review bandwidth are actually uncovered?
- Is the crate healthy only in the narrow sense of “publishes sometimes”, or does it have legible stewardship across the work that keeps it usable?

## Suggested work classes for `0.1`

### Keep-the-lights-on
- `issue_triage`
- `bug_fix_response`
- `ci_breakage_response`
- `security_incident_response`
- `performance_regression_response`
- `dependency_upkeep`
- `documentation_freshness`

### Enable-evolution
- `design_or_vibe_check`
- `pull_request_review`
- `refactor_capacity`
- `contributor_enablement`
- `release_orchestration`

## What it is not

### 1. Not the maintenance window by itself

A crate can honestly say “critical fixes only” or “reactive maintenance” and still leave unclear whether CI failures, perf regressions, docs drift, or PR review are actually covered.
Maintenance-coverage asks **which work classes** are really owned.

### 2. Not succession / backup posture by itself

A crate can have a named backup maintainer and still have no visible owner for docs upkeep or contributor review.
Succession asks **who could carry the crate next**.
Maintenance coverage asks **what work is currently covered now**.

### 3. Not imported trust or registry signals

Security tabs, trusted publishing, SLOC, and `pubtime` are useful imported signals.
They do not prove who will triage issues next week or who will review a risky refactor.

### 4. Not a social score or maintainer-fund substitute

This seam should not become a moral score, a funding-allocation algorithm, or a leaderboard of invisible labor.
It stays at the contract/report layer.

## Working rule for future passes

When a future pass sharpens **P-0011**, it must say explicitly whether it is adding:

1. **broad health-profile truth**,
2. **maintenance-window truth**,
3. **succession-map truth**,
4. **support-intent truth**,
5. **maintenance-coverage truth**,
6. or **health-check consistency truth**.

Do **not** let the archive quietly rephrase “reactively maintained”, “trusted publishing only”, “no advisories shown”, or “single maintainer with backup” into a fake claim that the crate’s actual invisible maintenance work is broadly covered.

## Sources

- https://blog.rust-lang.org/inside-rust/2026/01/12/what-is-maintenance-anyway/
- https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- https://blog.rust-lang.org/2026/01/21/crates-io-development-update/
- https://doc.rust-lang.org/cargo/reference/manifest.html#the-badges-section
- https://github.com/rust-lang/crates.io/issues/2437
