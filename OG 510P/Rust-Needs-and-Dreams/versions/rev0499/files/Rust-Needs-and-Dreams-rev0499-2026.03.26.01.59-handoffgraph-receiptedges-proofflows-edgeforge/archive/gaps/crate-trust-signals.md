# Gap: crate trust still lacks a portable evidence-and-policy surface

## Summary
Rust now has serious trust-relevant building blocks:
- crates.io security UX and Trusted Publishing controls,
- RustSec advisories,
- `cargo-vet` audits and importable audit criteria,
- lifecycle signals and maintenance heuristics,
- release evidence such as signatures, SBOMs, and provenance,
- and registry/search UX that increasingly shapes dependency choice.

What it still lacks is a **shared trust boundary** that can answer, with evidence and without hand-wavy scoring:
- why a dependency is considered acceptable or risky,
- which trust signals are direct facts versus imported attestations versus local policy conclusions,
- which signals apply only to build dependencies or proc-macros,
- how fresh those signals are,
- and what changed between two lockfiles or two release candidates.

That missing layer is not “another ranking website”.
It is a portable report and pack boundary that lets Rust users, CI, and registries evaluate trust with explainable policy.

## Why now
Recent ecosystem changes have made this seam much more concrete:
- crates.io now has a Security tab showing RustSec advisories directly on crate pages, which means trust information is already moving into dependency-selection-time UX;
- crates.io Trusted Publishing has expanded: GitLab CI/CD is supported in addition to GitHub Actions, crate owners can require Trusted Publishing only, and some risky GitHub triggers are blocked outright;
- crates.io added `pubtime` to index entries so future tooling can reason about publication timing and cooldowns;
- `cargo-vet` has a mature story for importable audits, decentralized sharing, built-in `safe-to-run` / `safe-to-deploy` criteria, and custom criteria like `crypto-reviewed`;
- crates.io’s malware-notification policy now leans more heavily on RustSec advisories for routine malicious-crate removals, which is sensible but also makes it more important not to confuse “has an advisory” with the entire trust story;
- community interest in crate reliability/ranking persists, but without a neutral evidence substrate the conversation keeps drifting toward opaque scores.

Sources:
- https://blog.rust-lang.org/2026/01/21/crates-io-development-update/
- https://blog.rust-lang.org/2026/02/13/crates.io-malicious-crate-update/
- https://mozilla.github.io/cargo-vet/how-it-works.html
- https://mozilla.github.io/cargo-vet/audit-criteria.html
- https://internals.rust-lang.org/t/adding-a-reliability-rating-system-to-crates-io/23567
- https://rust-lang.github.io/rfcs/1824-crates.io-default-ranking.html

## The current seam is awkward
Today, trust decisions are stitched together from incompatible fragments:
- crates.io UI signals,
- RustSec advisories,
- `cargo-vet` audits and imports,
- local allow/deny policy,
- ownership/publisher controls,
- CI provenance or signing artifacts,
- and README/social proof that is not machine-readable.

Those pieces do not yet form one reviewable story.
A team can often tell that *something* is true — “this crate uses Trusted Publishing”, “that version has an advisory”, “someone audited this dependency for `safe-to-deploy`”, “this package was published two hours ago”, “that proc-macro has no audit coverage” — but still struggle to turn that into:
- one lockfile-scoped trust report,
- one explainable verdict per dependency and dependency kind,
- one diff when trust posture changes,
- and one attachable artifact for CI/release/approvals.

This causes recurring failure modes:
- people collapse all signals into one opaque score;
- policy exceptions get buried in CI YAML or issue comments;
- build-time and proc-macro dependencies do not get scoped differently from runtime dependencies;
- imported human audits and registry facts are flattened together as though they had the same issuer and semantics;
- rankings drift into popularity theater because the underlying evidence boundary is weak.

## Why this matters
This gap affects more than security teams.
It helps:
1. **application teams** choose dependencies with explainable policy rather than folklore;
2. **maintainers** publish trust-relevant evidence without inventing custom dashboards;
3. **CI/release systems** attach trust posture to lockfiles and releases;
4. **registries and search UX** surface meaningful signals without becoming authoritarian scoreboards;
5. **policy tooling** consume provenance, advisories, audits, lifecycle, and freshness in one place;
6. **incident response** diff trust posture before and after malicious-crate events or emergency pins.

## Lane rule
Read this note together with [`design/trust-decision-lane-map.md`](../design/trust-decision-lane-map.md) so **registry discovery, advisory feeds, audit attestations, graph-policy lint, artifact recovery, local decisions, and thin consumer views** remain distinct instead of collapsing into one trust score.

## What “good” looks like
A worthy contribution here is a **trust evidence substrate** with at least:
- `trust-signal/v0` — one atomic signal with issuer, subject, scope, freshness, evidence, and explainable semantics;
- `trust-report/v0` — a lockfile/workspace report combining many signals without flattening them into one score;
- `trust-diff-report/v0` — what trust-relevant facts changed between two states;
- `trust-pack/v0` — an attachable bundle for CI, release, registry, and audit workflows;
- and a `cargo trust` CLI that can verify, diff, explain, and attach these artifacts.

Signals should be multi-dimensional, including at least:
- registry facts (security tab / publication timing / publisher control posture),
- advisories,
- audit attestations and criteria,
- provenance and release evidence,
- lifecycle inputs,
- typosquat/impersonation risk,
- and local policy exceptions.

The winning version is policy-driven, issuer-aware, scope-aware, and explainable — not one trust score to rule them all.
