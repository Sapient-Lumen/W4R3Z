## Current interpretation after rev0446
Read this contract now as the boundary beneath `design/publisher-source-identity-execution-blueprint-2026Q1.md`.
The execution blueprint does **not** replace this file; it sharpens its role.
This contract still owns the separation between **subject**, **claim**, **publisher authority**, **source route**, **source-hint / provenance-boundary**, and **consumer handoff** truth.

# Design: Publisher & Source Identity Contract (2026 Q1)

## Goal
Make Rust package identity reviewable by standardizing one thin boundary for **publisher authority**, **project-family / namespace claims**, **source route posture**, **best-effort source hints**, and **downstream handoffs**.

This contract is meant to sit *between* raw registry/package mechanics and downstream trust/admission/install consumers.
It is deliberately narrower than “solve package trust” and broader than “show owners in the UI”.

## Why this is a frontier now
The current crates.io/Cargo direction is no longer just “add nicer registry UX later”.
It is actively creating **new kinds of identity and authority facts** that downstream tools need to preserve instead of flattening:

- crates.io now supports Trusted Publishing for multiple CI providers, adds Trusted-Publishing-only mode, and blocks risky GitHub Actions triggers; publish authority is therefore increasingly issuer-backed and policy-shaped, not just token-shaped.
  - https://blog.rust-lang.org/2026/01/21/crates-io-development-update/
  - https://rust-lang.github.io/rfcs/3691-trusted-publishing-cratesio.html
- Cargo is explicit that named owners and team owners are not the same authority class: team owners can publish/yank but cannot add or remove owners.
  - https://doc.rust-lang.org/cargo/reference/publishing.html
  - https://doc.rust-lang.org/cargo/commands/cargo-owner.html
- Cargo’s registry web API says Cargo has no inherent global notion of users/owners beyond registry-defined handling.
  - https://doc.rust-lang.org/cargo/reference/registry-web-api.html
- authenticated alternate registries now carry credential-provider posture as part of the route, while source replacement is explicitly an **exact-copy equivalence** mechanism rather than “another registry”.
  - https://doc.rust-lang.org/cargo/reference/registry-authentication.html
  - https://doc.rust-lang.org/cargo/reference/registries.html
  - https://doc.rust-lang.org/cargo/reference/source-replacement.html
- optional namespaces are no longer just debate material: RFC 3243 exists and open namespaces remain an active Cargo/compiler/crates.io implementation seam.
  - https://rust-lang.github.io/rfcs/3243-packages-as-optional-namespaces.html
  - https://rust-lang.github.io/rust-project-goals/2025h2/open-namespaces.html
- `package.authors` is now explicitly de-centered: RFC 3052 made the field optional and moved crates.io/docs.rs UI toward current owners.
  - https://rust-lang.github.io/rfcs/3052-optional-authors-field.html
- `cargo package` can emit `.cargo_vcs_info.json`, but the docs explicitly say provenance is not verified.
  - https://doc.rust-lang.org/cargo/commands/cargo-package.html
- crates.io verification/mirroring work makes it increasingly important to keep **registry/source route truth** distinct from **publisher claim truth**.
  - https://rust-lang.github.io/rust-project-goals/2025h1/verification-and-mirroring.html
  - https://blog.rust-lang.org/inside-rust/2026/02/11/program-management-update-2026-01/

Taken together, these changes say Rust is missing a durable boundary for answering:

- who may publish;
- under what issuer/credential posture that happened;
- what family or namespace claim is being made;
- what route/source semantics were in play;
- where source hints stop and verified provenance does not begin; and
- what later consumers may honestly import.

## Core thesis
A worthy contribution here is **not**:

- one crate “trust score”,
- one registry badge system,
- one namespace solution that settles every governance argument,
- or one provenance story that silently upgrades hints into proof.

It is a contract that keeps five truths separate:

1. **claim truth** — what project/family/namespace relationship is being asserted;
2. **publisher-authority truth** — who may publish and under which authority class;
3. **source-route truth** — where the package came from and what route semantics applied;
4. **source-hint / provenance-boundary truth** — which source attachments are hints versus verified facts;
5. **consumer-handoff truth** — what trust, policy, package-admission, install, support, and incident tools may import without distortion.

## Why this is distinct from nearby frontiers
### Not the same as Package Intake Gateway
**Package Intake Gateway** begins when a package is extracted, staged, resolved, built, or installed locally.
The publisher/source identity contract is *upstream* of that. It describes how a package is identified and authorized before local intake logic decides whether to admit it.

### Not the same as Trust Decision Stack
**Trust Decision Stack** owns evidence aggregation and local verdicts.
The publisher/source identity contract only provides structured identity facts and route posture.
A trusted publisher is not automatically a trusted crate, and an exact-copy replacement source is not automatically the same thing as a policy-approved source.

### Not the same as Distribution Contract or Update Continuity
Those are downstream consumer surfaces: install, update, rollback, and support continuity.
They should import this contract rather than reinventing authority or claim semantics.

## The contract layers
### 1) Claim / family / namespace layer
This layer answers:
- is the subject a single crate, a family of crates, or a namespace-controlled subtree?
- is the grouping namespace-enforced, owner-curated, maintainer-declared, or merely inferred from naming?
- what is explicitly *not* being claimed?

This must preserve uncertainty and non-claim states.
`project-*` and `parent::child` are not equivalent facts.

### 2) Publisher-authority layer
This layer answers:
- who currently has publish authority?
- is the authority a named owner, a team owner, or an issuer-backed trusted publisher?
- are token-based publishes still possible, or is Trusted-Publishing-only mode enforced?

This must preserve the difference between “may publish” and “may govern owners”.

### 3) Source-route layer
This layer answers:
- did this package come from crates.io, an alternate registry, a local registry, vendoring, or a replacement source?
- if replacement is involved, is the route an exact-copy equivalence path?
- what auth / credential-provider posture applies?
- what index / API / download endpoints were relevant?

This must preserve the difference between **distinct registry** and **same-source mirror/equivalence route**.

### 4) Source-hint and provenance-boundary layer
This layer answers:
- which repository/VCS/package-side hints exist?
- which ones are self-declared or packaging-time best effort?
- which ones are registry-verified or cryptographically verified?

This is where `.cargo_vcs_info.json` belongs: useful, but never silently upgraded into provenance proof.

### 5) Consumer handoff layer
This layer answers:
- which facts may package-admission, trust, install, support, and incident tooling import?
- what lossiness occurs when importing into thinner views?
- what changes should generate diffs or review prompts?

## Proposed artifacts
The contract should be realizable as small portable artifacts rather than one platform rewrite.

### Core reports
- `claim-report/v0`
- `publisher-report/v0`
- `source-report/v0`
- `source-hint-report/v0`
- `publisher-source-pack/v0`
- `publisher-source-diff/v0`
- `publisher-source-handoff/v0`

### CLI surfaces
These can start as external commands:
- `cargo source report`
- `cargo source verify`
- `cargo publisher report`
- `cargo publisher diff`
- `cargo publisher handoff --to <consumer>`

## Ranked MVP shape
### 1. `source-report/v0` first
This is the best starting lane because it proves route semantics cleanly:
- crates.io vs alternate registry vs source replacement vs vendored path;
- sparse vs git registry posture where relevant;
- credential-provider and auth expectations;
- exact-copy replacement semantics.

Why first: it solves a real confusion today and is lower-governance than namespaces or org claims.

### 2. `publisher-report/v0` second
This proves publish authority without turning it into trust.
It should expose:
- named owner vs team owner differences;
- trusted-publisher presence;
- Trusted-Publishing-only status;
- issuer/provider identity;
- publish capability versus owner-management capability.

### 3. `claim-report/v0` third
Only after route and authority are clean should the stack encode family claims.
It should support:
- namespace-controlled family;
- owner-curated family;
- maintainer-declared family;
- inferred / uncertain family;
- no claim.

### 4. Handoffs fourth
Once route/authority/claim reports exist, attach them to:
- package-admission review;
- install receipts;
- support packs;
- incident/reconstruction views.

### 5. Diffs and alerts fifth
Only then should the stack add continuity features like:
- owner changes;
- Trusted-Publishing-only flips;
- issuer changes;
- registry/route changes;
- namespace/family claim changes.

## What the worthy contribution looks like in practice
In theory, this contribution gives the ecosystem a precise ontology for package identity.
In practice, it should feel like this:

- a maintainer can answer “how is this crate allowed to publish?” without reading registry-specific lore;
- a reviewer can see whether a package came from a distinct alternate registry or an exact-copy replacement path;
- a registry UI can show family/namespace posture without overclaiming provenance or trust;
- package-admission tooling can import authority/source facts without redefining them;
- an incident responder can diff what changed in identity posture between two versions;
- install/support tooling can preserve *how* a package arrived, not just what version was installed.

## Strategic rank
This should be treated as the clearest next **publication / identity / source-route-shaping** seam.
It belongs near the supply-chain band, but it is not the same thing as intake, policy, trust, or install.

Recommended placement in the ladder:
- keep **Package Intake Gateway** as the local-ingress seam;
- promote **Publisher & Source Identity Contract** as the upstream publication/authority/route seam;
- keep **Trust Decision Stack** as the downstream local-verdict seam.

## What not to build
Do **not** turn this into:
- a universal registry-governance platform,
- a mandatory namespace policy,
- a single scalar trust score,
- a registry-only UI project with no portable artifacts,
- or a provenance system that treats packaging hints as cryptographic truth.

## Adjacent files
- `design/publisher-source-identity-stack.md`
- `design/org-identity-registry-ux-kit.md`
- `design/trust-decision-stack.md`
- `design/package-intake-gateway-2026Q1.md`
- `gaps/publisher-source-identity-authority-claims-and-source-posture-continuity.md`
- `proposals/epic-publisher-source-identity-stack.md`

## Bottom line
Rust has accumulated enough real identity surfaces that **not** separating them is now the larger problem.
The ecosystem does not just need better registry UI; it needs a portable contract for **claim + publisher authority + source route + provenance boundary + consumer handoff**.
