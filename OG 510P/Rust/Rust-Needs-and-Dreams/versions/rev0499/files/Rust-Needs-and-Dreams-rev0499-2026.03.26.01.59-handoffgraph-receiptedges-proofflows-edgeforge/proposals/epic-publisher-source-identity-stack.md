## Current interpretation after rev0446
This proposal should now be read as the implementation vehicle for the explicit **Publisher & Source Identity execution blueprint**.
The blueprint is the boundary and shape; this proposal is the build plan.

# Epic Proposal: Publisher & Source Identity Stack (`cargo source` + `cargo publisher` + `publisher-source-pack/v0`)

## Current interpretation after rev0406
This proposal should now be read as the implementation vehicle for the promoted **Publisher & Source Identity Contract**.
The contract is the boundary; this proposal is the build plan.

## One-sentence pitch
Make Rust package identity boring by standardizing a portable layer that keeps **project-family claims, publish authority, registry/source posture, source-hint boundaries, and downstream trust/admission/install handoffs** distinct instead of forcing every tool to tell its own incompatible story.

## What changed in rev0406
The proposal is now explicitly ranked as a separate seam from:
- **Package Intake Gateway** (local package ingress and staging);
- **Trust Decision Stack** (evidence + policy verdicts);
- **Distribution / install continuity** (consumer-side lifecycle);
- and raw namespace / org-ownership debate.

The MVP is therefore more strongly ordered:
1. `source-report/v0`;
2. `publisher-report/v0`;
3. `claim-report/v0`;
4. `source-hint-report/v0` plus handoffs;
5. stack-level diffs and consumer alerts.

# Epic Proposal: Publisher & Source Identity Stack (`cargo source` + `cargo publisher` + `publisher-source-pack/v0`)

## One-sentence pitch
Make Rust package identity boring by standardizing a portable layer that keeps **project-family claims, publish authority, registry/source posture, best-effort package/VCS hints, and downstream trust/admission/install handoffs** distinct instead of forcing every tool to tell its own incompatible story.

## Deliverables
- reference commands:
  - `cargo source`
  - `cargo publisher`
- schemas:
  - `source-report/v0`
  - `publisher-report/v0`
  - `claim-report/v0`
  - `publisher-source-pack/v0`
  - `publisher-source-diff/v0`
  - `publisher-source-handoff/v0`
- adapters/importers for:
  - crates.io owner / team-owner facts
  - Trusted Publishing posture imports
  - alternate-registry and source-replacement config imports
  - namespace / prefix / family claim imports
  - `.cargo_vcs_info.json` imports with explicit best-effort posture
- docs:
  - alternate-registry vs source-replacement guide
  - owner/team/trusted-publisher semantics guide
  - namespace-controlled vs maintainer-declared claim guide
  - package-admission handoff guide
  - install/support/incident identity handoff guide

## Why now (signals)
- crates.io now supports GitLab CI/CD for Trusted Publishing, allows crate owners to enforce Trusted-Publishing-only mode, and blocks risky GitHub Actions triggers. That means publish authority is increasingly issuer-backed and configuration-shaped rather than only token-shaped.
  https://blog.rust-lang.org/2026/01/21/crates-io-development-update/
- Cargo’s publishing docs and `cargo owner` docs are explicit that named owners and team owners do not have the same capabilities: named owners can add or remove owners, while team owners can publish or yank but cannot change the owner set.
  https://doc.rust-lang.org/cargo/reference/publishing.html
  https://doc.rust-lang.org/cargo/commands/cargo-owner.html
- The registry web API says Cargo itself has no inherent notion of users/owners beyond registry-defined handling, which is a strong signal that registries/source identity need an explicit handoff layer instead of being treated as universal built-ins.
  https://doc.rust-lang.org/cargo/reference/registry-web-api.html
- Cargo’s registry-authentication docs say authenticated alternate registries require a credential provider to avoid unknowingly storing unencrypted credentials on disk. That makes auth posture part of source identity, not just a config footnote.
  https://doc.rust-lang.org/cargo/reference/registry-authentication.html
- Cargo’s source-replacement docs define replacement sources in terms of exact-copy equivalence and explicitly say a replacement source is not allowed to have crates that are not also available from the original source. That means replacement is not just “another registry”.
  https://doc.rust-lang.org/cargo/reference/source-replacement.html
- RFC 3243 plus the active open-namespaces goal make namespace control a live Cargo/compiler/crates.io seam, while RFC 3052 made `package.authors` optional and shifted UI emphasis toward owners. Together, those changes make claim identity, owner identity, and manifest authorship impossible to treat as one field any more.
  https://rust-lang.github.io/rfcs/3243-packages-as-optional-namespaces.html
  https://rust-lang.github.io/rust-project-goals/2025h2/open-namespaces.html
  https://rust-lang.github.io/rfcs/3052-optional-authors-field.html
- `cargo package` includes `.cargo_vcs_info.json` but explicitly warns that the package provenance is not verified and the tarball is not guaranteed to match that VCS information. That is exactly the kind of best-effort source hint this stack should import honestly rather than silently upgrading into provenance.
  https://doc.rust-lang.org/cargo/commands/cargo-package.html

## Non-goals
- choosing one universal crates.io namespace or transfer policy;
- replacing Trust Signals, Policy, Package Admission, or Distribution with one mega identity engine;
- exposing secrets, auth tokens, or registry-private details in reports;
- pretending issuer-backed publishing alone is a trust verdict;
- pretending `.cargo_vcs_info.json` or repository links prove source provenance.

## Strategic value
This deserves promotion because it gives the archive a missing **identity continuity seam**.
With it:
- crate-family claims can stay useful without pretending every prefix or namespace is controlled the same way;
- package-admission and trust tooling can import authority/source posture without silently redefining it;
- install receipts and incident tooling can preserve how software actually reached a machine;
- Rust can keep evolving namespaces, registry UX, and publishing controls without forcing every downstream tool to rediscover the distinctions.

The prize is not a badge.
The prize is a durable record of **who may publish, what is being claimed, where packages came from, what auth/source posture applied, and what downstream consumers may honestly infer**.

## Proposed shape
Ship a narrowly scoped stack-level layer:
1. make `source-report/v0` the canonical source/auth posture artifact for crates.io, alternate registries, replacement sources, vendored sources, and local registries;
2. make `publisher-report/v0` the canonical publish-authority artifact for owner/team-owner/trusted-publisher posture;
3. make `claim-report/v0` the canonical project-family / namespace / curated-membership artifact with explicit uncertainty and non-claim states;
4. import `.cargo_vcs_info.json` and similar hints only as best-effort attachments, never as verified provenance;
5. emit stack-level diffs and handoffs for Trust Signals, Package Admission, Distribution, support, and incident consumers;
6. preserve explicit boundaries between authority facts, claims, source configuration, and downstream policy verdicts.

## Critical design bet
The critical bet is that **identity continuity becomes useful before governance convergence**.
That means:
- owner/team/trusted-publisher posture is reported even if registry policy evolves,
- claim posture stays useful even if namespaces remain partial or optional,
- source/auth posture stays useful even if registry and mirror tooling evolves,
- and later consumers import those facts without flattening them into one verdict.

Without that boundary, the stack either stays too thin to matter or bloats into a fake universal trust/governance platform.

## Milestones
1. **v0 source/auth posture lane**
   - `source-report/v0`
   - crates.io / alternate registry / replacement source / vendored examples
2. **v0.2 publisher-authority lane**
   - `publisher-report/v0`
   - owner vs team-owner vs trusted-publisher posture
3. **v0.3 claim / namespace lane**
   - `claim-report/v0`
   - namespace-controlled vs maintainer-declared vs uncertain claims
4. **v0.4 package / install handoff lane**
   - import into package-admission and install receipts
   - preserve source/auth/claim import lossiness explicitly
5. **v1 consumer handoffs**
   - trust / policy / support / incident / archaeology consumers
   - time-diff and change alerts for authority/source posture changes

## Execution order
Use [`design/publisher-source-identity-pilot-program.md`](../design/publisher-source-identity-pilot-program.md) as the stack-level rollout:
1. source identity and auth posture,
2. publisher authority posture,
3. claim / namespace posture,
4. package-admission handoff,
5. distribution/install consumer lane.

Use [`design/org-identity-registry-ux-kit.md`](../design/org-identity-registry-ux-kit.md) as the leaf-level substrate beneath it.

## Success metrics
- users can distinguish alternate registries from exact-copy replacements without reading Cargo internals;
- owner/team-owner/trusted-publisher posture can be imported by review tooling without being mistaken for trust verdicts;
- claim reports can express project-family identity without requiring namespace completion first;
- package-admission and install receipts can preserve authority/source posture instead of re-inventing it;
- the ecosystem gets one explainable identity continuity seam instead of five partially overlapping badge systems.
