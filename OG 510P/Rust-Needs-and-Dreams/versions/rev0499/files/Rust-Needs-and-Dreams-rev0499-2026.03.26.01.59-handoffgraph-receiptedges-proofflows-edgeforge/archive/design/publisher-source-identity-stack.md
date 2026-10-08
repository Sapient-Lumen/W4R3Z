## Current interpretation after rev0446
Read this stack now as the leaf-and-composition substrate beneath `design/publisher-source-identity-execution-blueprint-2026Q1.md`.
The execution blueprint does **not** replace this file; it sharpens its role.
This stack still owns the composition between org/claim UX, source posture, publisher authority, trust imports, package-admission imports, and distribution/support continuity.

# Design note: Publisher & Source Identity Stack (promoted in rev0406 as Publisher & Source Identity Contract)

## Current interpretation
Read this stack now as the leaf-and-composition substrate beneath `design/publisher-source-identity-contract-2026Q1.md`.
The contract promotion does **not** replace this file; it sharpens its role.
This stack still owns the composition between org/claim UX, source posture, publisher authority, trust imports, package-admission imports, and install/support continuity.

## Frontier meaning after rev0406
The frontier claim is now explicit:
- **Package Intake Gateway** remains the clearest local ingress / extraction / staging seam;
- **Publisher & Source Identity Contract** is now the clearest upstream **publication / authority / route-shaping** seam;
- **Trust Decision Stack** remains the clearest downstream **trust / policy consumer** seam.

Use this stack note when the revision is about how these leaves compose.
Use the contract note when the revision is about what the missing ecosystem contribution should look like as a first-class boundary.

## Current high-value distinction set
Future revisions should preserve all of these distinctions at once:
- claim / family / namespace posture;
- publisher authority posture;
- source route posture;
- source-hint vs verified provenance posture;
- trust/policy imports;
- package-admission imports;
- install/support/incident imports.

Default rule: do not let one registry badge, one namespace discussion, one trusted-publisher feature, or one mirror story silently impersonate the whole stack.

# Design note: Publisher & Source Identity Stack (Org Identity + Trust + Package Admission + Distribution)

## Goal
Define the **division of labor** between publisher identity, source identity, trust signals, package admission, and consumer installation so the archive has an explicit answer to a recurring ecosystem confusion:

> What is the difference between “belongs to project X”, “may publish”, “came from source Y”, and “we trust/allow it”?

This note does not create a replacement mega-kit.
It explains how existing and newly promoted pieces should compose:
- [`design/org-identity-registry-ux-kit.md`](./org-identity-registry-ux-kit.md)
- [`design/trust-signals-kit.md`](./trust-signals-kit.md)
- [`design/package-admission-stack.md`](./package-admission-stack.md)
- [`design/distribution-contract-stack.md`](./distribution-contract-stack.md)
- [`design/policy-kit.md`](./policy-kit.md)

## Why this note is needed now
Rust’s ecosystem now has meaningful identity-relevant facts on multiple planes:
- crates.io Trusted Publishing and Trusted-Publishing-only mode express issuer-backed publish authority, and current crates.io work has widened that lane to GitLab CI/CD while blocking risky triggers;
- authenticated alternative registries require explicit credential-provider posture, so source identity now includes auth-storage posture rather than only a registry URL;
- source replacement remains an *equivalence* mechanism, not a new authority layer, and Cargo’s docs are explicit that replacement sources must be exact copies, not arbitrary forks;
- optional namespaces are an accepted RFC and an active cross-team implementation goal, so family/namespace control is now a live seam rather than a hypothetical future feature;
- Cargo/docs.rs have already moved user-facing identity away from manifest authorship toward current owners, while `cargo package` makes best-effort VCS hints available but explicitly says they are not verified provenance.

That means the archive needs a sharper boundary than “org UX”.

## Design boundary sharpeners
- **Owner != author != publisher subject.** RFC 3052 made `package.authors` optional and moved crates.io/docs.rs UI toward current owners. A future identity layer must not silently fall back from missing authorship metadata to current ownership or to trusted-publisher subjects.
- **Source replacement != alternate registry.** Replacement is an exact-copy equivalence mechanism with stronger sameness assumptions than ordinary alternate-registry use. The reports should make that visible because mirrors, policy, and incident response care.
- **VCS hint != provenance proof.** `.cargo_vcs_info.json` is a useful hint and should be attached, but the docs explicitly say the source provenance is not verified.
- **Namespace/family claim != final trust verdict.** A crate family can be real, curated, or uncertain without that alone deciding whether to admit, install, or trust a package.

## Stack layers

### 1) Claim / project identity layer
This layer answers:
- “Which crates or prefixes are presented as one project family?”
- “Which claims are maintainer-declared, curated, namespace-enforced, or merely suggestive?”

Owner: **Org Identity & Registry UX Kit** through `claim-report/v0`.

Design rule: a project-family claim is **not automatically** publish authority.

### 2) Publish-authority layer
This layer answers:
- “Who may publish this package?”
- “Is that authority based on owners, trusted publishers, namespace control, or some combination?”

Owner: **Org Identity & Registry UX Kit** through `publisher-report/v0`.

Design rule: trusted-publisher posture is still an authority fact, not a final trust or policy verdict.

### 3) Source-identity layer
This layer answers:
- “Which registry/source/replacement path is in play?”
- “Is this an alternate registry, an exact-copy replacement, a vendored lane, or a local registry?”
- “What auth posture applies?”

Owner: **Org Identity & Registry UX Kit** through `source-report/v0`.

Design rule: alternate registry and source replacement must remain distinct because Cargo assigns them different semantics.

### 4) Trust / policy consumer layer
This layer answers:
- “Given the identity facts, how should we warn, require review, or fail?”

Owners:
- **Trust Signals Kit** for issuer-aware imported signals;
- **Policy Kit** for explainable rules, waivers, and decisions.

Design rule: trust/policy **imports** publisher/source identity; it does not redefine those facts.

### 5) Publish / package-admission / distribution consumer layer
This layer answers:
- “Under what authority/source posture was this package published?”
- “Under what authority/source posture was this package admitted?”
- “What path did an actual install select?”

Owners:
- **Publish Set Kit** for producer-side source-package publication truth;
- **Package Admission Stack** for registry-facing package-admission review;
- **Distribution Contract Stack** for consumer-side acquisition and install receipts.

Design rule: publication, admission, and installation remain separate events even when they share identity inputs.

## What an epic contribution should look like in practice
A worthy contribution here is not “namespaces, finally”.
It is a portable identity substrate with ranked consumers:
1. **source-report lane first**
   - prove registry vs replacement vs vendored truth and auth posture;
2. **publisher-report lane second**
   - prove publish-authority facts without turning them into trust scores;
3. **claim-report / namespace lane third**
   - prove project-family and namespace semantics can be reported without choosing one universal org model;
4. **package-admission handoff fourth**
   - attach authority/source posture to publish review;
5. **distribution/install consumer fifth**
   - attach source/claim imports to actual install receipts and incident/support consumers.

## Anti-goals
Do not turn this stack into:
- one universal org-verification badge,
- one stealth trust score,
- one forced namespace decision for every crate family,
- or one registry-management umbrella that absorbs distribution, policy, or package-admission layers.

The stack is about **identity truth and handoff boundaries**, not ecosystem centralization.

## Execution documents
- [`gaps/publisher-source-identity-authority-claims-and-source-posture-continuity.md`](../gaps/publisher-source-identity-authority-claims-and-source-posture-continuity.md)
- [`design/publisher-source-identity-pilot-program.md`](./publisher-source-identity-pilot-program.md)
- [`proposals/epic-publisher-source-identity-stack.md`](../proposals/epic-publisher-source-identity-stack.md)
