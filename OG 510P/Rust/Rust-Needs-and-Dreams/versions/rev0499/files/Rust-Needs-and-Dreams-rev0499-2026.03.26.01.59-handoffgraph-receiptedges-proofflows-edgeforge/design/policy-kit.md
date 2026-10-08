# Design: Policy Kit (`cargo policy`, `policy-pack/v0`)

## Goal
Create a unified, explainable policy workflow for Rust workspaces, lockfiles, and release candidates by defining:
- portable policy artifacts,
- a reference CLI (`cargo policy`) for evaluation, diffing, explanation, and waiver handling,
- and clear boundaries between **imported evidence**, **declared rules**, **evaluation results**, and **local exceptions**.

This is intentionally **not** a universal “crate score”.
It is a reviewable decision layer over heterogeneous evidence.

## Why this deserves to be a top-tier contribution
The Rust ecosystem is now producing many useful policy-relevant signals, but still leaves teams to stitch them together by hand:
- Rust’s 2026 flagship work explicitly includes **secure your supply chain**, with milestones around public/private dependencies and SBOM support.
- crates.io now surfaces a **Security** tab, stronger **Trusted Publishing** controls, blocked risky CI triggers, and publication timestamps in the index.
- `cargo vet` already models **criteria**, **project policies**, **trusted publishers**, imported audit sets, and date-bounded trust.
- `cargo-deny` already models licenses, advisories, bans, sources, targets, and check-specific exit codes.
- `cargo-audit` and `rustsec` already provide vulnerability scanning and advisory-database consumption.

What is still missing is the shared layer that says:
- **what evidence was considered**,
- **which rules applied to which scope**,
- **why a decision passed, warned, failed, or remained inconclusive**,
- and **what changed between one review point and the next**.

That is the job of Policy Kit.

## References (signals)
- Rust 2026 flagships: secure your supply chain, public/private dependencies, SBOM support
  https://rust-lang.github.io/rust-project-goals/2026/flagships.html
- crates.io development update (Jan 2026): Security tab, Trusted Publishing enhancements, blocked triggers, `pubtime`
  https://blog.rust-lang.org/2026/01/21/crates-io-development-update/
- Cargo Vet introduction / audit criteria / project policies / trusted entries / config
  https://mozilla.github.io/cargo-vet/
  https://mozilla.github.io/cargo-vet/audit-criteria.html
  https://mozilla.github.io/cargo-vet/specifying-policies.html
  https://mozilla.github.io/cargo-vet/trusted-entries.html
  https://mozilla.github.io/cargo-vet/config.html
- cargo-deny config / advisories / bans / licenses / exit codes
  https://embarkstudios.github.io/cargo-deny/checks/cfg.html
  https://embarkstudios.github.io/cargo-deny/checks/advisories/index.html
  https://embarkstudios.github.io/cargo-deny/checks/bans/index.html
  https://embarkstudios.github.io/cargo-deny/checks/licenses/cfg.html
  https://embarkstudios.github.io/cargo-deny/cli/check.html
- cargo-audit and rustsec docs
  https://docs.rs/crate/cargo-audit/latest
  https://docs.rs/rustsec/latest/rustsec/

## Design principles
1. **Evidence first, rules second, verdict third**
   - imported facts and attestations must remain inspectable;
   - policy rules must remain explicit;
   - verdicts must be derived and explainable.
2. **Scope is first-class**
   - runtime, build, dev, proc-macro, tool, target-specific, and release-artifact policy are not interchangeable.
3. **Freshness and validity windows matter**
   - advisories, trusted-publisher windows, cooldown periods, and baseline ages must be explicit.
4. **Inconclusive is a real outcome**
   - lack of evidence should not be silently converted into pass or fail.
5. **Waivers are policy artifacts, not shell-script folklore**
   - exceptions should be durable, owned, justified, and expiring.
6. **Policy should compose kits rather than replace them**
   - Policy Kit consumes Trust Signals, Lifecycle Ledger, Typosquat Guard, SBOM Evidence, Signed Binaries, Support Envelope, and other kits instead of absorbing them.

## Core artifact family

### 1) `policy-subject/v0`
Defines what is being evaluated.

Required fields:
- workspace identity / lockfile hash / VCS revision when available
- optional artifact/release identity
- toolchain identity
- selected configuration slice:
  - package set
  - target set
  - feature/profile slice
  - dependency-kind slice
- evaluation time

Design rule: a policy report must say **which slice of reality** it covered.

### 2) `policy-input-catalog/v0`
Records the evidence and imported inputs considered during evaluation.

Should enumerate:
- advisory sources and snapshot identities
- license graph/source snapshot
- ban/source-policy inputs
- imported `trust-pack/v0` / `lifecycle-pack/v0` / `inventory-pack/v0` / `name-risk-report/v0` / `binverify-report/v0`
- optional org-local overlays
- freshness/validity metadata per source
- unsupported or unavailable input classes

Design rule: policy must preserve **what it looked at** and **what it did not have**.

### 3) `policy-rule-catalog/v0`
Portable declaration of policy rules.

Rule families should include:
- `REQUIRE`
- `FORBID`
- `ALLOW_ONLY`
- `MAX_THRESHOLD`
- `COOLDOWN`
- `FRESHNESS`
- `MATCH_CRITERIA`
- `REQUIRE_EXPLANATION`
- `REQUIRE_WAIVER`
- `DIFF_ONLY`

Selectors should include:
- dependency kind (`runtime`, `build`, `dev`, `proc-macro`, `workspace-tool`)
- direct vs transitive
- package / workspace member / dependency edge
- target / cfg / artifact channel
- publisher / source / registry class
- signal or evidence class

Examples:
- fail if a runtime dependency has an unresolved RustSec vulnerability,
- warn if a build dependency is newly published and inside a cooldown window,
- require Trusted Publishing or explicit waiver for proc-macros,
- require `safe-to-deploy` for selected crypto crates,
- allow `safe-to-run` for internal tooling crates,
- ban multiple versions of selected high-impact crates,
- require explicit acknowledgment when a license changes relative to baseline,
- fail if a policy-critical evidence source is stale or unavailable.

Design rule: rules must be visible as rules, not reverse-engineered from opaque CLI flags.

### 4) `policy-waiver/v0`
A durable exception record.

Required fields:
- rule id(s)
- subject selector(s)
- owner / approver
- reason / justification
- expiry or review date
- linked evidence / ticket / incident / migration plan
- optional mitigation notes

Design rule: a waiver is neither a pass nor a hidden TODO.
It is a named, reviewable decision.

### 5) `policy-decision-report/v0`
The main evaluation artifact.

Should record:
- subject reference (`policy-subject/v0`)
- input reference (`policy-input-catalog/v0`)
- rules evaluated
- per-rule and per-subject outcomes:
  - `PASS`
  - `WARN`
  - `FAIL`
  - `INCONCLUSIVE`
  - `WAIVED`
  - `SKIPPED`
- reason codes
- affected packages/edges/scopes
- explanation chains with referenced evidence
- summary counts and exit-status mapping

Design rule: every non-pass outcome should be explainable in a few hops.

### 6) `policy-diff-report/v0`
Captures change between two decision points.

Should show:
- new/removed violations
- new/removed warnings
- evidence freshness changes
- new dependencies entering stricter scopes
- waiver additions / removals / expirations
- trust/lifecycle/inventory/advisory deltas that changed policy outcomes
- rule-set changes and their decision impact

Design rule: policy should be reviewable over time, not only at a single snapshot.

### 7) `policy-pack/v0`
Bundle format containing:
- `policy-subject/v0`
- `policy-input-catalog/v0`
- `policy-rule-catalog/v0`
- `policy-decision-report/v0`
- optional `policy-waiver/v0` entries
- optional `policy-diff-report/v0`
- attachments or content-addressed references

This is the artifact that should move through CI, release review, security review, and audit workflows.

## Reference UX: `cargo policy`
- `cargo policy init`
  - create starter rules with explicit scope sections instead of one flat config.
- `cargo policy check`
  - evaluate current workspace / lockfile / selected slice.
- `cargo policy report`
  - emit `policy-pack/v0` plus human-readable summary.
- `cargo policy explain <rule-or-subject>`
  - show evidence chain and why result is what it is.
- `cargo policy diff <old> <new>`
  - show what changed and why.
- `cargo policy waive`
  - create a typed waiver artifact with expiry and owner.
- `cargo policy verify`
  - validate pack integrity, source freshness bounds, and waiver expiry.

The CLI should begin as an **orchestrator and explainer**.
It should not try to replace cargo-deny, cargo-vet, rustsec, or registry features.

## Suggested adapter map
- **cargo-deny**
  - licenses, advisories, bans, sources, target-scoped dependency graph filtering, and machine-meaningful check classes
- **cargo-audit / rustsec**
  - advisory and binary-recovered inventory checks, especially when paired with auditable binaries
- **cargo-vet**
  - audit criteria, imported audit sets, publisher trust windows, and project-specific policy intent
- **Trust Signals Kit**
  - normalized trust evidence, issuer class, freshness, and explanation-ready inputs
- **Lifecycle Ledger Kit**
  - declared maintenance intent, support windows, and successor/handoff signals for policy consumption
- **Typosquat Guard Kit**
  - name-risk and impersonation warnings
- **SBOM Evidence Kit**
  - artifact-linked dependency scope inputs, especially for release-stage policy
- **Signed Binaries / Repro Build / Support Envelope kits**
  - distribution, rebuild, and supported-platform policy checks at release time

## Policy lattice model
Policy should admit multiple decision layers instead of one flat answer.

Recommended layers:
1. **Import layer**
   - what evidence sources were available and fresh enough?
2. **Rule layer**
   - what requirements apply to this subject/scope?
3. **Decision layer**
   - what verdict follows from the rule plus evidence?
4. **Exception layer**
   - was an explicit waiver applied?
5. **Presentation layer**
   - CI summary, PR diff, registry/admin view, audit-review worksheet

This keeps “missing evidence”, “policy says fail”, and “policy waived” from collapsing into the same bucket.

## High-value scenarios
1. **Proc-macro hardened policy**
   - require Trusted Publishing or explicit waiver,
   - fail on unresolved advisories,
   - warn on fresh publishes within cooldown window.
2. **Crypto-sensitive product**
   - require cargo-vet custom criteria like `crypto-reviewed` for selected crates,
   - fail if the imported audit set is stale,
   - allow narrow exceptions only with owner + expiry.
3. **Release candidate gate**
   - combine runtime inventory, support envelope, trust signals, and signed-binary evidence,
   - fail if release artifacts are missing required attached evidence.
4. **Large workspace split-risk policy**
   - `safe-to-deploy` for shipped services,
   - `safe-to-run` for internal tools,
   - different license/source constraints for build-only tooling.

## Overlap boundaries
- **Not Trust Signals Kit:** Trust standardizes evidence; Policy decides what to do with it.
- **Not Lifecycle Ledger Kit:** lifecycle intent feeds policy but is not itself a verdict.
- **Not SBOM Evidence Kit:** inventory is an input, not a policy result.
- **Not Incident Kit:** incidents may trigger or review policy changes, but incident response remains separate.
- **Not a registry mandate:** crates.io may surface policy-adjacent signals, but Policy Kit must work for private workspaces and org-local review flows too.

## Hard problems (explicitly scoped)
1. **Evidence heterogeneity**
   - advisories, trust entries, imported audits, licenses, source restrictions, and support claims are not semantically identical.
2. **Staleness vs failure**
   - stale or missing inputs should often be `INCONCLUSIVE`, not silently downgraded.
3. **Scope precision**
   - build dependencies and proc-macros often deserve stricter policy than dev-only crates.
4. **Rule churn**
   - policy changes themselves can create diff noise; the diff format must show rule-originated changes clearly.
5. **Exception debt**
   - waivers must be visible enough that organizations can ratchet them down over time.

## What the kit should provide to others
- **Release Pipeline Kit:** one attachable decision artifact for release candidates.
- **Trust Signals Kit:** a downstream consumer that preserves signal provenance.
- **Build Doctor / Change Impact / Migration Kits:** a place to route policy on upgrade urgency, waiver windows, or release blocks.
- **Ecosystem Atlas Kit:** bounded “recommended stack” or “allowed stack” views that remain explainable.
- **Agent / assistant tooling:** a durable machine-readable answer to “why did CI reject this dependency change?”

## Evaluation plan
Treat [`design/policy-pilot-program.md`](./policy-pilot-program.md) as the ranked execution order for Policy Kit. The first serious lane should be a **package release gate**, followed by **workspace split-scope policy**, **proc-macro/build-lane cooldown policy**, **artifact-linked release-candidate policy**, and finally a **migration diff / review lane**.

Success bar:
- every non-pass decision is explainable in a few hops,
- stale or missing evidence is surfaced honestly,
- waivers are explicit and expiring,
- rule changes are diffable,
- and multiple evidence-producing kits can compose without being flattened into one fake compliance number.
