# Design note: Trust Decision Stack (Trust Signals + Policy + registry/review consumers)

## Goal
Define the **division of labor, lane boundaries, and consumer flow** between trust-relevant evidence and trust/policy decisions so Rust can improve supply-chain trust without collapsing everything into one fake crate score, one cargo-vet clone, one cargo-deny wrapper, or one registry-controlled verdict.

This is **not** a new top-level kit.
It is a stack note explaining how existing archive pieces should compose:
- [`design/trust-decision-lane-map.md`](./trust-decision-lane-map.md)
- [`design/trust-signals-kit.md`](./trust-signals-kit.md)
- [`design/trust-signals-pilot-program.md`](./trust-signals-pilot-program.md)
- [`design/policy-kit.md`](./policy-kit.md)
- [`design/policy-pilot-program.md`](./policy-pilot-program.md)
- [`design/typosquat-guard-kit.md`](./typosquat-guard-kit.md)
- [`design/lifecycle-ledger-kit.md`](./lifecycle-ledger-kit.md)
- [`design/signed-binaries-kit.md`](./signed-binaries-kit.md)
- [`design/sbom-evidence-kit.md`](./sbom-evidence-kit.md)

## Lane rule
The stack should now be read through [`design/trust-decision-lane-map.md`](./trust-decision-lane-map.md). The concrete rule is that **registry discovery**, **advisory feeds**, **audit attestations**, **graph-policy lint**, **artifact recovery**, **local policy decisions**, and **thin consumer views** are all real but different lanes. A stack-level summary may compose them, but it must not erase their issuer, subject, scope, or derivation differences.

## Why this note is needed now
Rust’s current signals are no longer saying only “supply-chain trust matters in principle.” They are saying the ecosystem now has **enough real signal families** that the missing problem is orchestration and separation of concerns:
- crates.io now exposes a Security tab, `pubtime`, GitLab Trusted Publishing, Trusted Publishing-only mode, and blocked risky GitHub Actions triggers;
- the crates.io malicious-crate policy now routes most malware removals through RustSec advisories instead of repetitive incident blog posts, which raises the value of local diffable artifacts over ambient public noise;
- Cargo Vet already models imported audits, criteria semantics, subtree-sensitive policy, violations, and audit backlogs;
- Cargo publishing remains permanent, so release-time trust review is not hypothetical or reversible;
- the 2026 flagships keep supply-chain work active through public/private dependency and SBOM milestones.

Together these signals justify treating trust as a **stacked execution seam** rather than a vague “security metadata” cluster.

## Stack layers

### 1) Trust Signals: issuer-aware facts and attestations
Trust Signals owns the **evidence substrate**:
- registry facts and publisher-control posture;
- advisory-feed facts;
- imported audit attestations and criteria semantics;
- local graph-policy-lint imports when used;
- artifact-recovery imports when the subject is a built artifact;
- lifecycle and successor inputs;
- signing / provenance / reproducibility imports when available;
- name-risk / typosquat findings;
- freshness windows and cooldown-relevant timestamps;
- explanation chains and diffable trust posture.

Trust answers questions like:
- “Which trust-relevant facts do we have for this lockfile or release candidate?”
- “Which issuer said what, at what scope, and how fresh is it?”
- “What changed in trust posture between these two states?”

Design rule: **trust evidence is not yet a policy verdict**.
A registry fact, an imported audit, a RustSec advisory, and a local exception are not interchangeable.

### 2) Policy: explicit rules, waivers, and decisions
Policy owns the **decision layer**:
- rule catalogs;
- subject scope;
- waiver budgets;
- `PASS` / `FAIL` / `INCONCLUSIVE` / `WAIVED` outcomes;
- consumer-specific handoff rules.

Policy answers questions like:
- “Given this evidence mix, may we publish?”
- “Do build dependencies need stricter cooldowns than runtime dependencies?”
- “Did this fail because of stale evidence, a real advisory, or a rule change?”

Design rule: **policy imports trust; it does not redefine trust schemas**.
`cargo trust` should not become a second policy engine just because trust decisions are one major consumer.

### 3) Registry/search/review presentation
Some trust outputs will be shown in registries, code review, CI, or search UX.

This layer decides:
- which trust artifacts are rendered directly versus summarized;
- which thin views are useful for discovery or release review;
- when advisory or freshness warnings should be shown without pretending to be a final verdict;
- how registry-side experiences remain views over portable artifacts instead of becoming the source of truth.

Design rule: **presentation must stay thinner than the evidence and decision layers**.
A crates.io panel, search badge, or PR comment is not the canonical trust record.

### 4) Downstream consumers
The stack becomes worthy when real consumers can import it without flattening it:
- **Policy Kit** can make explicit package/release/workspace decisions;
- **Release Pipeline Kit** can attach trust posture to release candidates;
- **Migration Kit** can diff trust posture across upgrades instead of only comparing versions;
- **Ecosystem Atlas Kit** can use trust as one visible dimension without becoming a ranking oracle;
- **Incident workflows** can compare before/after trust posture and name-risk signals;
- **registry/search UX** can surface explainable views without inventing a global score.

Design rule: **consumers import selected evidence or decisions; they do not collapse the stack into one scalar number**.

## What an epic contribution should look like in practice
A worthy contribution here is not “make crates.io show better scores.”
It is a portable, reviewable stack with clear boundaries:

1. **Signal first**
   - publish `trust-signal`, `trust-report`, `trust-import-profile`, and `trust-diff-report` cleanly;
2. **Build/proc-macro separation second**
   - prove trust scope matters in lockfile review rather than only at runtime;
3. **Policy handoff third**
   - feed the existing Policy Kit with explicit imported trust evidence instead of one ad hoc summary;
4. **Release attachment fourth**
   - attach trust posture to release candidates and artifact review;
5. **Registry/search views fifth**
   - only then add discovery-facing views or ranking-like overlays, and keep them explainable and optional.

## Ranked first execution lanes
1. **Lockfile trust-report lane**
   - best first exporter because it proves issuer/scope/freshness separation without needing a policy engine.
2. **Build / proc-macro split lane**
   - proves trust scope affects real decisions instead of only report prose.
3. **Publisher-control and freshness lane**
   - makes Trusted Publishing posture, `pubtime`, and cooldown semantics concrete.
4. **Release-candidate attachment lane**
   - ties trust to real release/admission workflows.
5. **Registry/search/review consumer lane**
   - proves thin views can stay honest rather than becoming de facto truth engines.

## Non-goals
- one scalar crate-trust number;
- replacing Cargo Vet, RustSec, or registry security work;
- a single registry-mandated verdict model;
- making `cargo trust` the owner of waivers, approvals, and release gates;
- turning incident blog posts or social chatter into the trust substrate.


## Execution documents
Treat this stack note, [`design/trust-decision-pilot-program.md`](./trust-decision-pilot-program.md), and [`proposals/epic-trust-decision-stack.md`](../proposals/epic-trust-decision-stack.md) as one execution band.
This file defines the boundary, the pilot program defines the rollout order, and the epic proposal defines what a worthy ecosystem contribution would look like in product form.

## Archive implications
- The archive should now treat **Trust Signals + Policy** as a coupled **Trust Decision Stack** in frontier discussions, with Typosquat Guard, Lifecycle Ledger, Signed Binaries, and SBOM Evidence as imported companions rather than collapsed sub-kits.
- Future revisions should prefer **ranked trust pilots, explicit policy handoff, build/proc-macro scope honesty, and thin explainable views** over another crate-score idea or another single-tool replacement pitch.
- When Atlas, Release Pipeline, Migration, or registry UX work cites trust posture, it should distinguish **signal truth**, **policy truth**, and **rendered views**.

## References (signals)
- Rust in 2026 / flagship themes:
  https://rust-lang.github.io/rust-project-goals/2026/flagships.html
- crates.io development update:
  https://blog.rust-lang.org/2026/01/21/crates-io-development-update/
- crates.io malicious-crate notification policy update:
  https://blog.rust-lang.org/2026/02/13/crates.io-malicious-crate-update/
- Cargo publishing reference:
  https://doc.rust-lang.org/cargo/reference/publishing.html
- Cargo Vet: how it works / criteria / policies / performing audits:
  https://mozilla.github.io/cargo-vet/how-it-works.html
  https://mozilla.github.io/cargo-vet/audit-criteria.html
  https://mozilla.github.io/cargo-vet/specifying-policies.html
  https://mozilla.github.io/cargo-vet/performing-audits.html
