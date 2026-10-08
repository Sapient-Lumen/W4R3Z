# Design: Trust Signals Pilot Program

## Purpose
Turn **Trust Signals Kit** into an executable rollout instead of leaving it as a strong but underspecified evidence concept.

The archive already has the right raw thesis: Rust needs issuer-aware, scope-aware, freshness-aware trust artifacts instead of another crate score.
What it did **not** yet answer clearly enough is:
- which trust exports should be standardized first,
- how trust should stay distinct from policy decisions,
- which signal mixes are mature enough to compose immediately,
- when build/proc-macro scope needs stricter handling than runtime scope,
- and what counts as a successful pilot rather than a nicer dashboard.

A worthy contribution here is not just `cargo trust report`.
It is a ranked pilot plan that proves trust artifacts survive real lockfile churn, release review, policy handoff, and registry-facing rendering without flattening issuers or scopes.

## References (signals)
- Rust’s 2026 flagships keep supply-chain work concrete through public/private dependencies and SBOM milestones, which means policy-facing dependency evidence remains an active first-class problem rather than an enterprise side quest.
  https://rust-lang.github.io/rust-project-goals/2026/flagships.html
- The crates.io development update added a Security tab, GitLab Trusted Publishing, Trusted Publishing-only mode, blocked risky GitHub Actions triggers, and `pubtime`. That means registries are now emitting enough machine-usable trust facts that a portable trust report can be more than a thought experiment.
  https://blog.rust-lang.org/2026/01/21/crates-io-development-update/
- The crates.io malicious-crate policy update says the team will usually publish RustSec advisories rather than noisy blog posts for every malware removal. That increases the value of local attachable trust artifacts and diffable reports.
  https://blog.rust-lang.org/2026/02/13/crates.io-malicious-crate-update/
- Cargo’s publishing reference is explicit that publishes are permanent. That raises the value of trust posture review before release rather than after the fact.
  https://doc.rust-lang.org/cargo/reference/publishing.html
- Cargo Vet already proves the ecosystem has mature trust inputs: built-in `safe-to-run` / `safe-to-deploy`, imported audits, subtree-sensitive policy, violations, and audit-backlog guidance. The missing contribution is the portable substrate above these point tools, not another scanner.
  https://mozilla.github.io/cargo-vet/how-it-works.html
  https://mozilla.github.io/cargo-vet/audit-criteria.html
  https://mozilla.github.io/cargo-vet/specifying-policies.html
  https://mozilla.github.io/cargo-vet/performing-audits.html

## Design principles
1. **Pilot evidence lanes before trust views.** Start with portable artifacts, not registry badges.
2. **Keep policy handoff explicit.** Trust reports should feed `cargo policy`, not secretly become a second policy engine.
3. **Build/proc-macro scope must be first-class early.** Supply-chain concern is not uniform across dependency kinds.
4. **Freshness is part of the subject.** A report without timestamp/cooldown semantics is not enough.
5. **Issuer conflicts stay visible.** Imported audits, advisories, registry facts, and local annotations should not silently collapse.
6. **Views must remain thin.** Search or registry rendering should come late and stay explainable.
7. **Graduation requires a real consumer.** A pilot succeeds only when policy, release, review, or registry UX can consume it honestly.

## Artifact family
### 1. `trust-pilot-brief/v0`
Why a trust lane is being piloted.

Should record:
- pilot id and summary
- subject family (`lockfile-report`, `scope-split`, `publisher-freshness`, `release-attachment`, `registry-view`)
- why this lane matters now
- intended consumers and action paths
- why the pilot is tractable now

### 2. `trust-import-profile/v0`
The allowed trust-evidence mix for a pilot.

Should record:
- imported signal families
- issuer classes and provenance expectations
- freshness and cooldown rules
- allowed missing-data posture
- conflict-resolution posture
- whether an import is canonical, advisory, local-only, or derived

Design rule: **this is not a verdict profile**.
It declares the evidence mix, not what a release gate must decide.

### 3. `trust-view-profile/v0`
How trust results may be rendered for humans.

Should record:
- consumer class (`pr-review`, `publisher-ci`, `registry-view`, `search`, `migration-review`)
- fields and slices rendered directly
- what must stay linked rather than summarized
- whether scores are forbidden or merely optional
- required explanation depth

Design rule: **rendering limits are part of honesty**.
Not every consumer should see the same compression.

### 4. `trust-consumer-handoff/v0`
How a consumer uses trust artifacts.

Should record:
- which trust artifacts are consumed directly
- whether Policy Kit is also required
- what local assumptions the consumer adds
- whether human approval is mandatory
- which conclusions the consumer must not claim

### 5. `trust-pilot-scorecard/v0`
Decides whether the pilot works.

Should ask:
- did the pilot keep issuer, scope, and freshness truth intact?
- did at least one consumer use it without bespoke scraping?
- did it stay distinct from policy decisions?
- did it keep build/proc-macro and runtime scope honest?
- did it improve explainability without inventing a score?
- does widening the pilot still look justified?

### 6. `trust-pilot-pack/v0`
Bundle for review and reuse:
- pilot brief
- trust import profile
- trust view profile
- consumer handoff
- `trust-report` / `trust-diff-report` / attachments
- scorecard and references

## Ranked first pilots

### 1) Lockfile trust-report lane
**Why first**
- It is the smallest lane that still proves issuer-aware, scope-aware, freshness-aware reporting.
- It gives policy, migration, and review workflows something durable to consume before any registry UI experiments.
- It avoids prematurely deciding what a verdict engine should do.

**Core artifacts**
- `trust-report/v0`
- `trust-import-profile/v0`
- optional `trust-diff-report/v0`
- `trust-pilot-pack/v0`

**Primary consumers**
- code review
- local CI reporting
- migration diff tools

### 2) Audit-attestation and split-scope lane
**Why second**
- Rust’s supply-chain risk is not uniform across runtime, build, and proc-macro dependencies.
- Cargo Vet’s criteria and policy model already make this distinction operationally useful.
- This pilot proves the stack can say “more scrutiny here” without becoming a policy engine itself.

**Core artifacts**
- scope-aware trust report slices
- import profile with compile-time-sensitive rules
- view profile for PR/review contexts
- diff report highlighting scope changes

**Primary consumers**
- application teams
- proc-macro-heavy workspaces
- policy handoff lanes

### 3) Publisher-control / freshness / graph-policy-lint lane
**Why third**
- crates.io now exposes Trusted Publishing posture and `pubtime`, making publisher/freshness truth much more usable than before.
- This is the first lane that turns registry facts into reviewable trust posture rather than ambient UI facts.
- It is also where cooldown semantics become concrete.

**Core artifacts**
- publisher-control trust signals
- freshness/cooldown fields in trust reports
- diff report for recent-publish changes
- consumer handoff to policy/release review

**Primary consumers**
- publisher CI
- dependency intake review
- org-level trust dashboards that remain thin views

### 4) Artifact/release attachment lane
**Why fourth**
- By this point the trust pack should be stable enough to travel with real release candidates.
- This pilot composes with Signed Binaries, SBOM Evidence, and Release Pipeline without swallowing them.
- It is a strong test of whether trust posture can remain attachable evidence rather than a hidden gating script.

**Core artifacts**
- release-linked `trust-pack/v0`
- optional artifact-recovery imports from `cargo audit bin` / `cargo-auditable` when the subject is a built binary
- imported signature / SBOM / lifecycle signals where present
- trust diff against prior release candidate
- consumer handoff to policy or release review

**Primary consumers**
- release engineering
- artifact intake review
- downstream packagers

### 5) Registry/search/review consumer lane
**Why fifth**
- This is where the ecosystem is most tempted to flatten trust into a score.
- Delaying it forces the archive to prove the evidence and handoff layers first.
- It is still important, because better registry/search/review UX is one reason to build the substrate at all.

**Core artifacts**
- trust view profiles for registry/search/PR contexts
- explicit compression rules
- linked explanation chains
- scorecard measuring whether the view stays honest

**Primary consumers**
- registry/search UX experiments
- assistant/guide layers
- review bots and dependency dashboards

## Honest partial outcomes
A pilot may still succeed if it only proves one of these:
- lockfile trust reports are much more valuable than registry views,
- build/proc-macro splitting matters more than generalized scoring,
- publisher/freshness signals are useful inputs but should stay advisory,
- release-linked trust packs help even if registry rendering remains thin,
- `cargo trust` should stay a substrate/orchestrator while `cargo policy` remains the only verdict engine.

## Failure modes to avoid
- inventing a score before proving evidence and handoffs
- making `cargo trust` a stealth policy engine
- flattening imported audits, advisories, registry facts, and local annotations into one claim
- pretending runtime, build, and proc-macro scope deserve identical treatment
- making registry/search rendering the canonical artifact boundary

## Archive policy
Future revisions should prefer:
- issuer-aware reports,
- explicit trust import profiles,
- early build/proc-macro scope honesty,
- policy handoff artifacts,
- and thin explainable views

over another crate-score debate, another cargo-vet replacement idea, or another registry-only UX proposal.
