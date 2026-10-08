# Crate health artifact completeness plan — 2026-03-22

This note deepens **P-0011 Crate Health Contract Kit** around a specific product question:

> once crates.io and GitHub expose more stewardship-adjacent substrate, what exact artifacts should a crate-health kit emit so another person can review support posture without flattening imported signals into promises?

## Product stance

The crate should stay reviewer-facing and read-first.
It should not become a hosted help desk, maintainer score, or social-performance dashboard.
It should emit compact artifacts that let a maintainer, downstream adopter, platform curator, or successor answer:

- which stewardship facts were declared by maintainers,
- which ones were only imported from registry or host-platform substrate,
- what changed in routing or continuity across time,
- and what still requires manual review.

## New first-class artifacts

### `registry-signal.import.json`

For each imported signal, record:

- source (`crates_io`, `github_repo`, `github_api`, `manual_import`, ...),
- signal kind (`security_tab_present`, `trusted_publishing_only`, `pubtime_available`, `sloc_visible`, `codeowners_present`, `private_vulnerability_reporting_enabled`, ...),
- mutability / freshness posture,
- whether the signal informs context, routing, continuity, or only security posture,
- and explicit notes on what it **does not** prove.

### `routing-drift.diff.json`

Across two stewardship snapshots, record:

- changed work routes,
- added or removed channels,
- continuity-backstop changes,
- owner-class changes,
- repository transfer or host-surface changes,
- and review notes explaining which changes are only host/import changes versus genuine support-contract changes.

### `health-support-bundle.manifest.json`

For one portable bundle, record:

- declared artifacts,
- imported artifacts,
- manual-review gaps,
- optional lineage / snapshot references,
- and whether the bundle is safe to share externally or only inside a team.

## CLI / workflow sketch

- `cargo crate-health capture` — existing capture flow, now optionally emitting registry-signal imports and a support-bundle manifest.
- `cargo crate-health import` — collect host/registry substrate while keeping exact provenance and mutability explicit.
- `cargo crate-health diff` — compare two health bundles and classify changes as declared-routing changes, imported-context changes, continuity changes, or manual-review-only.
- `cargo crate-health doctor` — flag false reassurance patterns such as “trusted publishing exists but no release route is declared” or “CODEOWNERS exists but release/docs/security routing is still missing.”

## Receiver-facing value

### For maintainers
See whether repository settings and crates.io features are helping downstream users or merely being over-read.

### For downstream adopters
Receive one bundle that distinguishes support promises from surrounding host-platform clues.

### For platform teams
Detect when routing or continuity posture actually changed, rather than assuming a crate stayed equally maintainable because its repository still looks polished.

### For successors or org transfers
Carry forward a stewardship bundle that explains what support routing survives the transfer and what needs re-declaration.

## MVP boundaries

### Include
- crates.io Security-tab / Trusted Publishing Only Mode / SLOC / `pubtime` imports.
- GitHub CODEOWNERS / private vulnerability reporting / repository-transfer-aware routing drift.
- one portable support-bundle manifest.
- conservative drift classes.

### Exclude
- SLA tracking.
- donation/funding analytics.
- social ranking of maintainers.
- hosted support inboxes or issue routers.

## Good first fixture set

1. A crate with Security tab, Trusted Publishing, and private vulnerability reporting that still lacks release/docs routing clarity.
2. An org-transfer event where collaborators persist, but continuity/backstop claims still need a routing drift artifact.
3. A portable bundle that joins declared routing, imported host facts, and explicit manual-review gaps for downstream review.

## Sources

- https://blog.rust-lang.org/inside-rust/2026/01/12/what-is-maintenance-anyway/
- https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- https://blog.rust-lang.org/2026/01/21/crates-io-development-update/
- https://rustfoundation.org/strategic-plan/
- https://docs.github.com/articles/about-code-owners
- https://docs.github.com/articles/about-pull-request-reviews
- https://docs.github.com/code-security/security-advisories/guidance-on-reporting-and-writing/privately-reporting-a-security-vulnerability
- https://docs.github.com/en/enterprise-cloud@latest/code-security/how-tos/report-and-fix-vulnerabilities/configure-vulnerability-reporting/configuring-private-vulnerability-reporting-for-a-repository
- https://docs.github.com/en/repositories/creating-and-managing-repositories/transferring-a-repository
- https://docs.github.com/en/enterprise-cloud@latest/rest/repos/repos
