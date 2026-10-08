# Gap: trust decisions still lack a portable evidence-to-policy handoff

## Summary
Rust now has enough **trust-relevant signal families** that the remaining missing layer is no longer just the evidence substrate.
What is still missing is the **reviewable handoff** from:
- trust signals and imported attestations,
- to explicit project policy and waivers,
- to thin consumer views in CI, release review, registry/search UX, and adoption briefs.

The ecosystem can already answer fragments such as:
- “this crate version has a RustSec advisory,”
- “this publisher or CI lane is Trusted Publishing-backed,”
- “this package was published recently,”
- “this dependency subtree is covered by imported `cargo vet` audits,”
- or “this project treats build and proc-macro dependencies differently.”

What it still struggles to answer cleanly is:
- which of those are raw facts versus imported attestations versus local decisions,
- which scopes were judged differently,
- why a verdict was `PASS`, `FAIL`, `INCONCLUSIVE`, or `WAIVED`,
- what changed between two review points,
- and which compressed registry/review/adoption views are allowed to claim what.

That missing layer is not “another score” and not “make `cargo trust` the policy engine.”
It is a **portable trust-decision boundary** that keeps evidence, rules, decisions, and rendered views distinct.

## Why now
Recent ecosystem changes make this much more concrete than it used to be:
- crates.io now shows RustSec advisories directly on crate pages via the Security tab;
- crates.io Trusted Publishing has expanded to GitLab CI/CD, TP-only mode, and blocked risky GitHub Actions triggers;
- crates.io added `pubtime` to index entries so tools can reason about freshness and cooldown posture;
- the crates.io malware-notification policy now routes routine malicious-crate removals through RustSec advisories as the durable record;
- Cargo Vet already has enough structure to prove that trust is not one dimension: custom criteria, imported audits, trusted publishers with date windows, subtree-sensitive policy, and multi-repository aggregation;
- Cargo publishing remains permanent, so evidence-to-policy review before publication matters.

Sources:
- https://blog.rust-lang.org/2026/01/21/crates-io-development-update/
- https://blog.rust-lang.org/2026/02/13/crates.io-malicious-crate-update/
- https://doc.rust-lang.org/cargo/reference/publishing.html
- https://mozilla.github.io/cargo-vet/how-it-works.html
- https://mozilla.github.io/cargo-vet/config.html
- https://mozilla.github.io/cargo-vet/trusted-entries.html
- https://mozilla.github.io/cargo-vet/multiple-repositories.html
- https://rust-lang.github.io/rust-project-goals/2026/flagships.html

## The current seam is awkward
Today, teams often improvise a trust decision from incompatible materials:
- crates.io UI facts,
- RustSec advisories,
- imported `cargo vet` audits,
- local policy rules and waivers,
- publisher/source identity,
- freshness or cooldown heuristics,
- lifecycle/maintenance signals,
- and optional release evidence like signatures or inventory attachments.

That usually leads to one of five failures:
1. evidence gets flattened into one opaque score or dashboard color;
2. trust and policy semantics get mixed, so a report silently becomes a verdict;
3. build/proc-macro/runtime scope differences disappear in the final summary;
4. registry/search/PR views overclaim what the underlying artifacts really proved;
5. migration/release/adoption consumers cannot diff or import the decision without re-scraping everything.

## Why this matters
This gap affects more than security teams.
It matters to:
1. **package-admission and release review** — because trust posture should attach cleanly to publish/release decisions;
2. **maintainers and orgs** — because waivers, cooldowns, and imported audits need durable reasoning artifacts;
3. **registry/search/review UX** — because thin views need honest compression rules;
4. **adoption guidance** — because ecosystem recommendations increasingly need reviewable trust posture, not folklore;
5. **incident response and migration** — because trust posture needs meaningful diffs across time.

## Lane rule
Read this note together with [`design/trust-decision-lane-map.md`](../design/trust-decision-lane-map.md) so **registry discovery, advisory feeds, audit attestations, graph-policy lint, artifact recovery, local decisions, and thin consumer views** remain distinct instead of collapsing into one trust score.

## What “good” looks like
A worthy contribution here is a thin composition layer above Trust Signals and Policy, with at least:
- `trust-decision-brief/v0` — why this review happened and for whom;
- `trust-decision-pack/v0` — linked evidence, rules, decisions, waivers, and bounded view profiles;
- `trust-decision-diff/v0` — what changed between two review points and why;
- `trust-decision-view/v0` — an explicit compressed rendering for PRs, registries, search, or adoption briefs;
- and a coordinating CLI/layer that can validate these attachments without absorbing the underlying trust or policy engines.

The winning version should keep these distinctions visible:
- **signal truth** versus **policy truth**,
- **issuer-backed facts** versus **local overlays**,
- **runtime/build/proc-macro scope**,
- **freshness/cooldown facts** versus **rule outcomes**,
- and **canonical artifacts** versus **thin consumer views**.

The bar is not a prettier dashboard.
The bar is a durable, explainable, importable decision boundary.
