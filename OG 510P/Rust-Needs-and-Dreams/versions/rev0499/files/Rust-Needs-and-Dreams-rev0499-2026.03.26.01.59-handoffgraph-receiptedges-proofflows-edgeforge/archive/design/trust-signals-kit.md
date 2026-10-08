# Design: Trust Signals Kit (`cargo trust`, `trust-pack/v0`)

## Goal
Standardize how Rust crates, lockfiles, and release candidates publish and consume trust-relevant evidence by defining:
- portable signal, report, import-profile, diff, and pack schemas,
- a reference CLI (`cargo trust`) for generating, diffing, verifying, and explaining trust reports,
- and clear boundaries between raw trust evidence, downstream policy decisions, and optional ranking/views.

This is intentionally **not** a universal crate score.
It is a contract for evidence plus explainable trust posture.

See also [`design/trust-decision-lane-map.md`](./trust-decision-lane-map.md) for the rule separating registry facts, advisories, audit attestations, graph-policy lint, artifact recovery, local decisions, and thin views; [`design/trust-decision-stack.md`](./trust-decision-stack.md) for the archive-level division of labor between Trust Signals and Policy; and [`design/trust-signals-pilot-program.md`](./trust-signals-pilot-program.md) for the ranked rollout.

## References (signals)
- crates.io development update (Jan 2026): Security tab, GitLab Trusted Publishing, Trusted Publishing only mode, blocked triggers, `pubtime` in the index
  https://blog.rust-lang.org/2026/01/21/crates-io-development-update/
- crates.io malicious-crate notification policy (Feb 2026)
  https://blog.rust-lang.org/2026/02/13/crates.io-malicious-crate-update/
- Cargo Vet “How it works”
  https://mozilla.github.io/cargo-vet/how-it-works.html
- Cargo Vet audit criteria
  https://mozilla.github.io/cargo-vet/audit-criteria.html
- Cargo Vet imports, trusted entries, and config
  https://mozilla.github.io/cargo-vet/importing-audits.html
  https://mozilla.github.io/cargo-vet/trusted-entries.html
  https://mozilla.github.io/cargo-vet/config.html
- cargo-deny checks / JSON output
  https://embarkstudios.github.io/cargo-deny/cli/check.html
  https://embarkstudios.github.io/cargo-deny/cli/common.html
- cargo-audit / cargo audit bin and cargo-auditable
  https://docs.rs/crate/cargo-audit/latest
  https://github.com/rust-secure-code/cargo-auditable
- RFC 1824 default ranking context
  https://rust-lang.github.io/rfcs/1824-crates.io-default-ranking.html
- Community reliability/verification discussion
  https://internals.rust-lang.org/t/adding-a-reliability-rating-system-to-crates-io/23567

## Design principles
1. **Signal first, policy second, ranking last**
   - raw facts and attestations should remain inspectable;
   - downstream policy may derive PASS/WARN/FAIL/INCONCLUSIVE;
   - any ranking/view must remain a thin, explainable interpretation.
2. **Issuer and scope are first-class**
   - registry facts, RustSec advisories, OIDC publishers, imported audits, local policy, and heuristics are not interchangeable.
3. **Dependency kind matters**
   - build dependencies, proc-macros, and runtime dependencies often deserve different trust thresholds.
4. **Freshness matters**
   - publication time, advisory age, policy expiry, and audit recency should be explicit.
5. **Artifact recovery is a distinct import lane**
   - lockfile review and built-binary recovery should not be narrated as the same subject.
6. **Local policy exceptions must be durable artifacts**
   - do not hide trust waivers inside shell scripts or CI YAML.

## Core components

### 1) `trust-signal/v0`
An atomic trust-relevant statement.

Required fields:
- `kind`:
  - `PUBLISH_PROVENANCE`
  - `PUBLISH_CONTROL`
  - `ADVISORY`
  - `AUDIT`
  - `LIFECYCLE`
  - `REPRODUCIBILITY`
  - `SIGNING`
  - `TYPO_RISK`
  - `POLICY_EXCEPTION`
  - `CONTEXT`
- `subject`:
  - crate/version/source identity
  - optional dependency-edge context
- `scope`:
  - `runtime`
  - `build`
  - `dev`
  - `proc-macro`
  - `workspace`
- `issuer`:
  - registry
  - RustSec
  - audit repository / organization
  - CI/OIDC publisher
  - local policy owner
  - external heuristic tool
- `verification_level`
- `freshness` / validity window when relevant
- `evidence` payload or content-addressed reference
- `reason_codes`
- short human explanation

Design rule: **a signal is not a verdict**.
It is one fact or attestation with explicit issuer and scope.

### 2) `trust-report/v0`
A lockfile- or workspace-scoped trust summary.

Should record:
- graph identity (lockfile hash / workspace digest)
- all relevant `trust-signal/v0` entries
- signal grouping by crate/version/scope
- imported `trust-import-profile/v0` reference or inline summary
- unresolved / missing / stale signal notes
- explanation chains in a small number of hops
- optional thin “view” metadata for search/registry/review UIs

Design rule: **keep raw signal classes visible even when a downstream policy emits one verdict**.

### 3) `trust-import-profile/v0`
A portable declaration of the trust-evidence mix.

Should support:
- which signal families are imported;
- issuer-class expectations;
- freshness / cooldown windows;
- missing-data posture;
- conflict-resolution posture;
- whether an import is canonical, advisory, local-only, or derived.

Examples:
- accept registry publisher-control facts and RustSec advisories as canonical, but treat name-risk results as advisory;
- import Cargo Vet audits with preserved criteria semantics and direct-import provenance;
- import cargo-deny graph-policy outputs as local lint results rather than pretending they are global facts;
- import artifact-recovery results only when the subject is a built binary or release artifact;
- declare that recent-publish facts are advisory inputs to policy rather than self-executing failures.

Design rule: **import profiles are not verdict policies**.
They declare what evidence mix a report is built from, not what a release gate must decide.

### 4) `trust-diff-report/v0`
Structured change report between two states.

Should record:
- new or removed advisories
- publisher control changes
- audit coverage gains/losses
- lifecycle changes flowing into trust results
- freshness/cooldown changes
- new exceptions or expired exceptions
- verdict changes (`PASS -> WARN`, `WARN -> FAIL`, etc.)

Design rule: trust posture should be reviewable over time, not only point-in-time.

### 5) `trust-pack/v0`
Bundle format containing:
- `trust-report/v0`
- optional `trust-import-profile/v0`
- optional `trust-diff-report/v0`
- raw evidence attachments / references
- signatures or provenance about the report itself when desired

This is the artifact that should move through CI, release review, registry experiments, and policy approval workflows.

### 6) `cargo trust`
Reference UX:
- `cargo trust report`
- `cargo trust verify`
- `cargo trust explain`
- `cargo trust diff`
- `cargo trust attach`
- `cargo trust import-profile`

`cargo trust` should start as an orchestrator / validator / explainer.
It should not try to replace Policy Kit, RustSec, cargo-vet, registries, or signing/provenance tools.

## Suggested signal mappings
- **crates.io Trusted Publishing / Trusted Publishing only mode / blocked triggers / `pubtime`:** publish-control and freshness signals
- **RustSec advisories / crates.io Security tab:** advisory signals
- **cargo-vet audits / imported audits / criteria / trusted publisher windows:** audit signals
- **cargo-deny advisories / bans / licenses / sources:** imported graph-policy-lint signals with local-config posture preserved
- **`cargo audit bin` / `cargo-auditable`:** artifact-recovery signals when the subject is a built binary
- **Lifecycle Ledger Kit outputs:** lifecycle signals
- **Signed Binaries / provenance / reproducibility kits:** signing and reproducibility signals
- **Typosquat Guard outputs:** typo-risk or impersonation-risk signals

## What the kit should provide to others
- **Policy Kit:** one structured source of trust inputs and import-profile truth rather than bespoke parsers.
- **Lifecycle Ledger Kit:** keep lifecycle as its own source-of-truth while letting trust consume it.
- **Incident Kit:** diff trust posture before/after malicious crate events.
- **Release Pipeline Kit:** attach `trust-pack/v0` to release candidates.
- **Org Identity & Registry UX Kit:** verify and render publisher/owner/source trust information.
- **Ecosystem Atlas Kit:** use explainable trust views without becoming a ranking oracle.

## Lane rule
This kit should now be read together with [`design/trust-decision-lane-map.md`](./trust-decision-lane-map.md). In particular, do not flatten **registry discovery**, **advisory feeds**, **audit attestations**, **graph-policy lint**, **artifact recovery**, **local decisions**, and **thin views** into one fake trust verdict.

## Overlap boundaries
- **Not Policy Kit:** policy consumes trust signals and import profiles but should remain the owner of verdicts, waivers, and decision reports.
- **Not Lifecycle Ledger Kit:** lifecycle remains distinct and feeds trust as one dimension.
- **Not Incident Kit:** incidents use trust evidence; they do not replace it.
- **Not a ranking website:** rankings may be derived views, not the canonical artifact.
- **Not a registry mandate:** crates.io may surface or consume these signals, but the kit should stand on its own.

## Hard problems (explicitly scoped)
1. **Issuer heterogeneity**
   - registry facts, advisories, imported audits, and local exceptions are not semantically identical.
2. **Scope heterogeneity**
   - runtime, build, and proc-macro trust decisions differ materially.
3. **False precision pressure**
   - the ecosystem will be tempted to compress trust into a scalar.
4. **Freshness and cooldown semantics**
   - recent publishes, audit age, and advisory recency need honest treatment.
5. **Privacy and sharing limits**
   - some trust evidence may be private or org-internal; sharing should be opt-in.

## Execution posture
- Execute this as part of the ranked trust rollout in [`design/trust-signals-pilot-program.md`](./trust-signals-pilot-program.md).
- Treat this as the evidence half of the broader Trust Decision Stack in [`design/trust-decision-stack.md`](./trust-decision-stack.md).
- Start with lockfile/workspace trust reports and scope-sensitive splits before registry/search views or richer release-gate consumers.

## Evaluation plan
Follow the pilot program:
1. lockfile trust-report lane,
2. build/proc-macro split-scope lane,
3. publisher-control and freshness lane,
4. release-candidate attachment lane,
5. registry/search/review consumer lane.

Success bar:
- issuer, scope, and freshness truth stay intact,
- trust posture changes are diffable,
- at least one downstream policy or release consumer can use the artifacts without bespoke scraping,
- and multiple signal families compose without being flattened into a fake universal score.
