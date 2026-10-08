# Design: Policy Pilot Program (`cargo policy pilot`, `policy-pilot-pack/v0`)

## Goal
Turn **Policy Kit** from the archive’s strongest governance concept into a ranked rollout program that proves real value quickly:
- import heterogeneous evidence without flattening it,
- evaluate explicit rules on explicit subjects,
- preserve waivers and `INCONCLUSIVE` outcomes honestly,
- and attach reviewable policy packs to the places Rust users already make decisions.

The archive already argues that policy is one of the highest-leverage seams in ideal Rust. The missing layer is now more practical:
- which policy subjects should be standardized first,
- which evidence imports are mature enough to compose immediately,
- where release-time policy and workspace-time policy should stay separate,
- how waivers and freshness windows should be introduced without theater,
- and what counts as a successful pilot rather than a nice-looking CI wrapper.

A worthy contribution here is not just `cargo policy check`. It is a disciplined pilot plan that proves a few high-value policy lanes can survive real review, drift, and exception handling before the kit widens into bigger organizational or ecosystem views.

## References (signals)
- Rust’s 2026 flagships explicitly frame supply-chain work around **public/private dependencies**, **breaking change detection**, and **SBOM generation**, which means release and dependency governance are active first-class goals rather than niche enterprise add-ons.
  https://rust-lang.github.io/rust-project-goals/2026/flagships.html
- The crates.io development update added a Security tab, expanded Trusted Publishing, exposed `pubtime`, and continued improving source/docs discoverability. That means crates.io is emitting richer governance-relevant facts than it did even a year ago.
  https://blog.rust-lang.org/2026/01/21/crates-io-development-update/
- Cargo’s publishing reference makes the core release fact unusually stark: a publish is permanent, versions cannot be overwritten, and code cannot be deleted. That raises the value of explicit release-admission policy and diffable exceptions.
  https://doc.rust-lang.org/cargo/reference/publishing.html
- The crates.io malicious-crate notification-policy update says the team is reducing blog-post noise and pushing toward more calibrated response/notification practice. That increases the value of local, attachable policy artifacts rather than relying on public incident posts as the governance surface.
  https://blog.rust-lang.org/2026/02/13/crates.io-malicious-crate-update/
- The 2025 malicious-crates post (`faster_log`, `async_println`) is a reminder that real-world registry risk is not hypothetical and that reviewable provenance, freshness, and exception handling matter.
  https://blog.rust-lang.org/2025/09/24/crates.io-malicious-crates-fasterlog-and-asyncprintln/
- `cargo vet` already has built-in criteria (`safe-to-run`, `safe-to-deploy`), subtree-sensitive policy configuration, trusted entries, and diff-oriented audit workflows. That proves the ecosystem already has serious policy ingredients, but not yet one common decision layer.
  https://mozilla.github.io/cargo-vet/audit-criteria.html
  https://mozilla.github.io/cargo-vet/specifying-policies.html
  https://mozilla.github.io/cargo-vet/trusted-entries.html
  https://mozilla.github.io/cargo-vet/performing-audits.html
- `cargo-deny` already exports structured checks for advisories, bans, licenses, and sources, with explicit config and machine-readable exit classes. That is more evidence that the missing contribution is orchestration/explanation, not another scanner.
  https://embarkstudios.github.io/cargo-deny/checks/cfg.html
  https://embarkstudios.github.io/cargo-deny/checks/advisories/cfg.html
  https://embarkstudios.github.io/cargo-deny/checks/bans/index.html
  https://embarkstudios.github.io/cargo-deny/checks/licenses/index.html
  https://embarkstudios.github.io/cargo-deny/cli/check.html

## Why this needs its own design layer
The Policy Kit already defines the base artifact family: subject, input catalog, rule catalog, waiver, decision report, diff report, and pack.

What it did **not** yet answer clearly enough is:
- which policy subjects deserve to be piloted first,
- which evidence mixes are stable enough to compose immediately,
- where rule changes should be treated differently from evidence changes,
- how waiver budgets and cooldown windows should be introduced,
- and when a policy pilot should be considered successful.

Without that layer, policy work risks two bad outcomes:
1. **CI glue drift** — lots of bespoke shell logic and dashboards, no durable artifact boundary;
2. **compliance theater** — a tool emits `FAIL`, but no one can cleanly answer whether the reason was an advisory, a missing audit, a stale import, a rule change, or an expiring waiver.

## Design principles
1. **Pilot concrete decision points, not abstract “security posture”.** Start where maintainers and release engineers already need an answer.
2. **Keep subject identity explicit.** Workspace policy, package policy, artifact policy, and release policy are related but not identical.
3. **Prefer evidence imports that already have structured semantics.** Build the decision layer above serious inputs instead of inventing new scanners.
4. **Treat `INCONCLUSIVE` as a first-class outcome.** Missing, stale, or incomparable evidence should not be hidden behind optimistic defaults or forced failures.
5. **Waivers need budgets, not just prose.** A pilot should make expiry, owner, and scope explicit.
6. **Rule churn must stay visible.** Policy diffs should distinguish evidence changes from rule changes.
7. **Graduation requires a real downstream consumer.** A pretty report is not enough if no release, review, or migration workflow actually uses it.

## Artifact family
### 1. `policy-pilot-brief/v0`
Why this decision point is being piloted.

Should record:
- pilot id and summary
- subject family (`package-release`, `workspace-split`, `proc-macro-cooldown`, `artifact-release`, `migration-diff`)
- why this decision point matters now
- intended consumers and action paths
- why the pilot is tractable now

### 2. `policy-slice-template/v0`
The declared policy slice for a pilot.

Should record:
- subject kinds allowed
- evidence classes required / optional
- rule families in scope
- out-of-scope rule families
- required verdict vocabulary
- unsupported or deferred semantics

Design rule: **do not smuggle the policy slice into prose**.
If a pilot depends on subject or rule boundaries, make them artifacts.

### 3. `evidence-import-profile/v0`
The allowed evidence mix for a pilot.

Should record:
- imported tools / feeds / packs
- freshness windows and cooldown rules
- source provenance expectations
- conflict-resolution posture
- missing-evidence behavior
- whether imports are canonical, advisory, local-only, or derived

Design rule: **import provenance is part of the contract**.
The same rule on two different evidence mixes is not the same policy lane.

### 4. `waiver-budget/v0`
The explicit exception model for a pilot.

Should record:
- waiverable rule families
- owner / approver requirements
- expiry model
- max-scope rules
- whether waivers downgrade `FAIL` to `WAIVED` or only annotate `WARN`
- whether waivers may be stacked or inherited

Design rule: **waivers are policy objects, not comments in CI**.

### 5. `policy-consumer-handoff/v0`
How the pilot result is consumed.

Should record:
- consumer class (`publisher-ci`, `workspace-governance`, `release-review`, `migration-review`, `security-review`)
- which decision artifacts are consumed directly
- what local assumptions the consumer adds
- whether human approval is required
- what the consumer must not claim on top of the pack

Design rule: **consumer power should be explicit**.
A release gate and a migration explainer do not need the same verdict model.

### 6. `policy-pilot-scorecard/v0`
Decides whether the pilot works.

Should ask:
- did the pilot preserve subject, rule, and evidence truth honestly?
- did at least one real workflow consume it?
- did it distinguish `FAIL`, `INCONCLUSIVE`, and `WAIVED` clearly?
- did it keep rule changes distinct from evidence changes?
- did it make waivers easier to review rather than easier to hide?
- does widening the pilot still look justified?

### 7. `policy-pilot-pack/v0`
Bundle for review and reuse:
- pilot brief
- policy slice template
- evidence import profile
- waiver budget
- consumer handoff
- policy artifacts from the base kit
- current scorecard
- references and rendered summaries

## Ranked first pilots

### 1) Package release gate
**Why first**
- Cargo publishes permanent versions, so package-release admission is a real decision point with durable consequences.
- crates.io is already surfacing security and trusted-publishing signals.
- This is the smallest lane that still exercises imported evidence, explicit rules, waivers, and diffable results.

**Core artifacts**
- `policy-subject/v0` for one package release
- `policy-input-catalog/v0` importing advisory/license/source/trust evidence
- `policy-rule-catalog/v0` for release-admission rules
- `policy-decision-report/v0`
- optional `policy-waiver/v0`
- bundled as `policy-pack/v0`

**Primary consumers**
- publisher CI
- release reviewers
- downstream packagers checking whether to ingest now or wait

### 2) Workspace split-scope policy
**Why second**
- Large Rust workspaces frequently need different rules for shipped products, internal tools, test-only crates, and build-only lanes.
- `cargo vet` and `cargo-deny` already prove subtree- and category-sensitive policy matters.
- This pilot proves Policy Kit can model different decision scopes without flattening them into one repository-wide verdict.

**Core artifacts**
- subject slices for `runtime`, `build`, `dev`, and `internal-tool` lanes
- import profile with scope-aware evidence rules
- decision diff separating rule drift from dependency drift
- waiver budgets that cannot silently leak across slices

**Primary consumers**
- monorepo owners
- org-level policy teams
- migration/release reviewers comparing one slice against another

### 3) Proc-macro / build-lane cooldown policy
**Why third**
- Freshly published or newly trusted crates are often much more sensitive in compile-time lanes such as proc-macros and build dependencies.
- crates.io trusted-publishing improvements and security metadata make these rules increasingly practical.
- This is where policy starts composing with compile-time-capabilities and trust signals in a way users can actually act on.

**Core artifacts**
- scope-aware subject marking compile-time lanes explicitly
- import profile with freshness / cooldown windows
- rules that distinguish runtime deps from build/proc-macro deps
- waiver budget with narrow scope and short expiry

**Primary consumers**
- security-sensitive application teams
- CI gates for proc-macro-heavy workspaces
- review workflows that want explainable heightened scrutiny

### 4) Artifact-linked release candidate policy
**Why fourth**
- By this point the pack should be stable enough to reason not just about the workspace, but about what is actually being released.
- This pilot composes Policy Kit with SBOM Evidence, Signed Binaries, Repro Build, and Support Envelope rather than treating them as unrelated efforts.
- It is a strong test of whether Policy Kit can stay a decision layer instead of swallowing all neighboring kits.

**Core artifacts**
- release/artifact subject identity
- imported SBOM, signature, rebuild, and support evidence
- decision reports with explicit `INCONCLUSIVE` handling for missing attachments
- policy diff against prior release candidates

**Primary consumers**
- release engineering
- security/reliability review
- artifact intake / deployment governance

### 5) Migration diff / dependency-change review lane
**Why fifth**
- Migration PRs are where teams most often need an explainable answer to “why did this dependency change become blocked?”
- This pilot proves Policy Kit is useful before and after release, not only at release time.
- It is also the right place to test human-readable explanation quality and diff semantics under real churn.

**Core artifacts**
- before/after policy subjects
- evidence imports for both sides
- explicit rule-change versus dependency-change diff
- waiver carry-forward rules and expiry checks

**Primary consumers**
- reviewers of upgrade PRs
- migration tooling
- assistant/bot workflows that need durable explanation artifacts

## What should wait
Do **not** start with a global crates.io ranking or a one-number ecosystem policy score.
Those are downstream views at best, and they would push the kit toward false precision before the decision artifacts are proven.

Also avoid starting with fully general enterprise policy catalogs. The first job is to make a few concrete Rust-native decision points legible and reusable, not to ship a universal compliance framework.

## Immediate archive decision
Treat [`design/policy-kit.md`](./policy-kit.md) and [`proposals/epic-policy-kit.md`](../proposals/epic-policy-kit.md) as the schema/epic anchors, and treat this file as the **execution order** for the next serious Policy work. The next credible move is not another scanner or dashboard; it is making `policy-pack/v0` survive Package Release Gate and Workspace Split-Scope Policy honestly.
