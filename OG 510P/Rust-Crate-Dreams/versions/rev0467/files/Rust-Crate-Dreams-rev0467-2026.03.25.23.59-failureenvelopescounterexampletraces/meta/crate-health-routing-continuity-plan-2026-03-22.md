# Crate Health Contract Kit — routing & continuity plan (2026-03-22)

This note sharpens **P-0011 Crate Health Contract Kit** into a more operational next pass.

## Main judgment

A worthwhile next implementation pass should **not** add more ranking heuristics, a maintainer leaderboard, or a funding score.
It should add the **operational stewardship layer** that tells other people how maintenance work actually flows.

The missing value is the boring contract above today’s:

- health-profile words,
- maintenance-window promises,
- succession notes,
- crates.io signals,
- CODEOWNERS hints,
- issue templates,
- `SECURITY.md` prose,
- and private vulnerability-reporting settings.

## What the crate should provide other people

For maintainers, downstream adopters, platform teams, and pathfinder/policy tooling, the crate should now provide:

1. **One work-routing report** instead of guessing from issues, labels, or CODEOWNERS.
2. **One response-channel receipt** instead of mixing public issue filing, discussions, email, and private security intake into one fuzzy “contact us” note.
3. **One continuity-backstop report** instead of bus-factor folklore or blind trust in org ownership.
4. **One conservative distinction between declared, imported, inferred, and manual-review-only routes**.
5. **One portable health bundle** that explains how the crate is supposed to stay responsive when real maintenance work arrives.

## Three new first-class review objects

### 1. Work-routing report

`work-routing.report.json` should answer:

- which route each work class takes,
- whether the route is public, private, mixed, or manual-review-only,
- which owner class is expected to respond,
- whether a backup route exists,
- and what evidence basis supports the claim.

Recommended work classes for `0.2`:

- `issue_triage`
- `bug_fix_response`
- `ci_breakage_response`
- `security_incident_response`
- `performance_regression_response`
- `dependency_upkeep`
- `documentation_freshness`
- `pull_request_review`
- `release_orchestration`

### 2. Response-channel receipt

`response-channel.receipt.json` should answer:

- what kind of channel this is (`public_issue_tracker`, `discussion_forum`, `private_security_reporting`, `direct_email_alias`, `manual_review_required`),
- what audiences and work classes it is for,
- whether confidential material is allowed,
- whether structured intake exists,
- and what escalation or fallback posture applies.

### 3. Continuity-backstop report

`continuity-backstop.report.json` should answer:

- whether support continuity depends on one primary person,
- whether an organization, team, rotation, backup maintainer, or successor process can keep the crate responsive,
- what absence window or degradation posture is explicitly admitted,
- and whether the backstop is declared, imported, inferred, or still unclear.

## Recommended command surface

### `cargo crate-health capture`
Capture maintainer-authored and imported signals and emit:
- `health-profile.report.json`
- `maintenance-window.report.json`
- `succession-map.report.json`
- `support-intent.report.json`
- `maintenance-coverage.report.json`
- `work-routing.report.json`
- `response-channel.receipt.json` (0 or more)
- `continuity-backstop.report.json`
- `registry-signal.import.json`

### `cargo crate-health check`
Run conservative consistency checks and flag:
- route gaps,
- public/private mismatches,
- routes that rely on one person with no backstop,
- and coverage claims with no visible intake path.

### `cargo crate-health diff`
Compare two health bundles and show when routing, channels, or continuity posture changed.

## Recommended importer posture

### Import, but keep distinct from declarations
- crates.io Security tab visibility
- trusted-publishing posture
- owners/teams on registry/repo
- CODEOWNERS and review-owner substrate
- private vulnerability-reporting availability
- maintainer-authored docs such as `SECURITY.md`, support docs, issue forms, or contribution notes

### Do not flatten into one fake answer
- “CODEOWNERS exists”
- “private vulnerability reporting exists”
- “there is an org owner”
- “issues are open”
- “trusted publishing is enabled”

Those are useful substrate facts, but not the same as a reviewable stewardship route.

## Preferred proving grounds

- a small crate with public issue routing, private security intake, and one explicit CI owner
- an org-owned crate with one primary maintainer but a team backstop during absence
- a crate where CODEOWNERS covers code review paths but says nothing useful about releases or security intake
- a quietly maintained crate that is honest about narrow routing and degraded response posture

## Design goals

1. **Operational, not judgmental** — help another person find the right route, not score the maintainers.
2. **Public/private honesty** — keep security/private intake separate from ordinary support channels.
3. **Backstop-first** — make continuity visible without demanding personal disclosures.
4. **Import-aware** — be honest about what comes from maintainer declarations versus host/repo substrate.
5. **Useful in absence** — the artifacts should still help when the primary maintainer is unavailable.

## Non-goals

- not a hosted support desk
- not an SLA dashboard
- not a funding allocation engine
- not a replacement for Trust Lens or security response tooling
- not a replacement for off-ramp / successor planning


## Artifact-completeness addendum

The lane now also needs three boring but receiver-critical artifacts:

- `registry-signal.import.json` so crates.io and host-platform stewardship-adjacent facts are portable without being over-read;
- `routing-drift.diff.json` so transfers, CODEOWNERS changes, or continuity edits are reviewable as changes in meaning rather than just host churn;
- `health-support-bundle.manifest.json` so another team can receive one compact stewardship packet instead of spelunking multiple host surfaces.

These artifacts should remain conservative about what they prove.
`private_vulnerability_reporting_enabled`, `trusted_publishing_only`, `pubtime_available`, or `codeowners_present` are all useful facts.
None of them should silently become “release route exists” or “maintained crate” verdicts.
