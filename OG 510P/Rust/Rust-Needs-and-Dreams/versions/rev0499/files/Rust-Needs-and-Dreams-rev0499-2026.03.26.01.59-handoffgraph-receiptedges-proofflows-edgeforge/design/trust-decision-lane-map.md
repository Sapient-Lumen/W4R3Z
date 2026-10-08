# Design: Trust Decision lane map (registry discovery, advisory feeds, audit attestations, graph-policy lint, artifact recovery, local decisions, thin views)

## Goal
Sharpen **Trust Signals Kit** and the broader **Trust Decision Stack** so the archive stops treating “Rust crate trust” as one bucket.
The live ecosystem now has several materially different trust-adjacent lanes, and they differ in **who issued the statement**, **what subject is being judged**, **whether the output is a raw fact, an attestation, a lint result, or a local verdict**, **which dependency scopes are in play**, and **how safely the result can be compressed for downstream consumers**.

The archive should therefore keep trust/admission work grounded in a lane map instead of one flattened “safe crate” story.

## Signals from the current ecosystem
- crates.io now surfaces a **Security** tab showing RustSec advisories directly on crate pages, supports Trusted Publishing from GitHub Actions and GitLab CI/CD, lets owners require **Trusted Publishing only**, blocks risky `pull_request_target` and `workflow_run` triggers, and records `pubtime` in index entries. That means registry discovery now emits trust-relevant facts at dependency-selection time instead of leaving them hidden in scattered docs or incident posts.
  https://blog.rust-lang.org/2026/01/21/crates-io-development-update/
- the crates.io team’s February 2026 malicious-crate policy update says routine malicious-crate removals will no longer get a blog post each time and that RustSec advisories are the durable public record in most cases. That is a strong signal that advisory feeds and ambient announcement/blog awareness are different lanes.
  https://blog.rust-lang.org/2026/02/13/crates.io-malicious-crate-update/
- RustSec presents itself as the Rust vulnerability database and explicitly points users to `cargo-audit`, `cargo-deny`, and `cargo-auditable`; it also exports advisory data to OSV and says GitHub Advisory Database imports its advisories. That means advisory facts already travel through several consumer channels with different semantics.
  https://rustsec.org/
- Cargo Vet documents imported audits, direct non-transitive trust relationships, built-in criteria like `safe-to-run` and `safe-to-deploy`, custom criteria, and trusted publisher entries with `start`/`end` publication windows. That makes audit attestations a real lane with issuer/scope/time semantics, not just another vulnerability feed.
  https://mozilla.github.io/cargo-vet/importing-audits.html
  https://mozilla.github.io/cargo-vet/audit-criteria.html
  https://mozilla.github.io/cargo-vet/trusted-entries.html
  https://mozilla.github.io/cargo-vet/config.html
- Cargo Vet also treats crates.io dependencies as auditable third-party code while path dependencies, git dependencies, and custom registries are generally trusted/first-party by default. That means subject classification is part of the lane map, not an afterthought.
  https://mozilla.github.io/cargo-vet/first-party-code.html
- cargo-deny keeps advisories, bans, licenses, and sources as distinct checks, supports JSON output, exposes bitset exit codes by check family, and lets projects filter graphs by workspace roots, dev-dependency posture, and target. That is a materially different lane from advisories alone or from imported human audits.
  https://embarkstudios.github.io/cargo-deny/cli/check.html
  https://embarkstudios.github.io/cargo-deny/cli/common.html
  https://docs.rs/cargo-deny
- `cargo audit` still focuses on RustSec-backed vulnerability checking, while `cargo audit bin` plus `cargo-auditable` create a post-build artifact-recovery lane where audit coverage depends on embedded dependency metadata rather than only the current lockfile. That should not be flattened into lockfile-trust review or source-selection UX.
  https://docs.rs/crate/cargo-audit/latest
  https://github.com/rust-secure-code/cargo-auditable

## The lanes

### 1) Registry discovery lane (selection-time registry facts)
This is the lane where trust-relevant facts are discovered directly from registry surfaces before or during dependency selection.

What defines it:
- crates.io Security-tab advisory visibility
- Trusted Publishing posture and Trusted-Publishing-only settings
- blocked-trigger / CI-provider posture
- `pubtime` and other registry metadata
- issuer = registry / registry-backed service

Why it deserves its own lane:
- these are selection-time facts, not a full verdict
- they arrive earlier than local audit or policy runs
- registry discovery is useful even when a project has not yet run local review tools

Design rule:
- keep registry discovery facts distinct from advisories, audit attestations, and local policy decisions

### 2) Advisory-feed lane (RustSec / OSV / GitHub Advisory / security-tab inputs)
This is the lane where the subject is “known issue information for a published package/version”, not “is this acceptable for my project”.

What defines it:
- RustSec advisory records
- OSV/GitHub Advisory import/export posture
- advisory class differences such as vulnerability versus unmaintained/unsound information
- version ranges, patched versions, and advisory freshness

Why it deserves its own lane:
- advisories are durable security/problem records, not local verdicts
- the same advisory may be visible through multiple consumers with different rendering rules
- a crate can have advisory facts without those facts being sufficient to decide project policy automatically

Design rule:
- keep advisory truth distinct from human audit attestations, graph-policy lints, and local pass/fail/waive decisions

### 3) Audit-attestation lane (`cargo vet` audits, criteria, imports, trusted publishers)
This is the lane where a project or organization says “someone we trust reviewed this dependency under explicit criteria”.

What defines it:
- built-in and custom criteria
- direct imports of other audit sets
- criteria maps and implication chains
- trusted publisher entries with time windows
- crate-scope / dependency-kind-sensitive policy requirements

Why it deserves its own lane:
- this is human attestation and delegation, not just feed ingestion
- Cargo Vet deliberately keeps imports direct and non-transitive so trust relationships stay understandable
- criteria and publication windows matter in ways a registry fact or advisory record does not capture

Design rule:
- keep audit-attestation truth separate from both advisory facts and local graph-policy lint results

### 4) Graph-policy lint lane (`cargo-deny` advisories / bans / licenses / sources)
This is the lane where the output is a structured local check result over the resolved dependency graph.

What defines it:
- advisories / bans / licenses / sources as separate check families
- target filtering, `--exclude-dev`, workspace-root posture
- JSON diagnostics and per-check exit-bit semantics
- local configuration-driven rule application

Why it deserves its own lane:
- this is already a multi-family review surface, not one scanner result
- a `cargo-deny` failure can mean very different things from a RustSec advisory or a missing cargo-vet audit
- license/source/bans posture often matters to admission even when no security advisory exists

Design rule:
- keep graph-policy lint results separate from registry facts, advisory records, and human audit attestations

### 5) Artifact-recovery lane (`cargo audit bin`, `cargo-auditable`)
This is the lane where trust review starts from built artifacts instead of from the current workspace lockfile alone.

What defines it:
- binary scanning via `cargo audit bin`
- embedded dependency metadata when artifacts were built with `cargo-auditable`
- partial recovery when artifacts lack auditable metadata
- linkage to shipped binaries and production environments

Why it deserves its own lane:
- this is the producer/consumer bridge for post-build or post-deploy review
- it answers a different question from “what does my current lockfile resolve to?”
- recovery quality varies materially depending on whether dependency metadata was embedded

Design rule:
- keep artifact recovery distinct from source-lockfile trust review and from release/installation conclusions built on top of it

### 6) Local decision / waiver lane (`cargo policy`, trust-decision packs)
This is the lane where imported facts and attestations become explicit project-local decisions.

What defines it:
- local policy rules
- waiver and cooldown posture
- subject scoping across runtime/build/dev/proc-macro lanes
- verdict classes such as `PASS`, `FAIL`, `INCONCLUSIVE`, and `WAIVED`
- diff reports explaining whether evidence changed, rules changed, or both

Why it deserves its own lane:
- this is where organizations turn evidence into action
- missing or stale evidence must be representable without pretending the raw evidence layer already decided the outcome
- package admission, dependency review, and adoption guidance all need this decision layer but should not redefine it independently

Design rule:
- keep local decisions and waivers distinct from the evidence that informed them

### 7) Thin consumer-view lane (registry/search/PR/adoption/assistant summaries)
This is the lane where trust posture is compressed for a specific downstream consumer.

What defines it:
- registry or search summaries
- PR bot summaries
- adoption briefs and assistant-facing projections
- explicit compression/profile rules
- visible links back to evidence and decisions

Why it deserves its own lane:
- this is where the ecosystem is most tempted to invent one fake crate score
- different consumers need different compression rules
- the most honest consumer views stay downstream and bounded rather than becoming the source of truth

Design rule:
- keep rendered views thin, explainable, and explicitly downstream of the canonical evidence and decision artifacts

## Cross-lane adapter risks
The archive should make at least these transitions explicit:
1. **registry discovery ↔ advisory feed**
   - a security-tab rendering is not the advisory database itself.
2. **advisory feed ↔ audit attestation**
   - “known issue information exists” is not the same statement as “a trusted reviewer certified this dependency under criteria X”.
3. **audit attestation ↔ graph-policy lint**
   - imported human audits and local deny-rules should not collapse into one hidden rule engine.
4. **lockfile review ↔ artifact recovery**
   - a lockfile report is not the same subject as a shipped binary scan.
5. **evidence lanes ↔ local decisions**
   - `PASS`/`FAIL`/`WAIVED`/`INCONCLUSIVE` must remain visibly derived from evidence instead of pretending to be raw facts.
6. **local decisions ↔ thin views**
   - registry/search/PR/adoption summaries should compress decisions and evidence, not replace them.

## What should change elsewhere in the archive
- **Trust Signals Kit** should own registry facts, advisory imports, audit-attestation imports, artifact-recovery imports, trust reports, diffs, and packs, but should cite this lane map as the rule for what must stay separate.
- **Policy Kit** should remain the owner of local rules, waiver budgets, and decision reports rather than re-owning advisory or audit semantics.
- **Trust Decision Stack** should import the lane map so evidence, lints, policy, and thin views remain explicitly layered.
- **Package Admission Stack** should import trust/advisory/audit/lint lanes plus policy results without silently turning them into one publish-side success color.
- **Dependency Review Stack** should import the same lanes for consumer-side intake and upgrade review, with explicit subject changes when the review target is a version bump or artifact-linked dependency.
- **Publisher & Source Identity Stack** should keep publisher/source claims as imported registry/issuer facts, not as full trust verdicts.
- **Adoption Decision Stack** should consume thin views and decision packs, not invent its own private trust score.
