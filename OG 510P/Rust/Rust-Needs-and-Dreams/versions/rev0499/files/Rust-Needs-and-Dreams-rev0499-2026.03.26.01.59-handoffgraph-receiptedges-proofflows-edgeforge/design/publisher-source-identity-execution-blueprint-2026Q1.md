# Design: Publisher & Source Identity execution blueprint (2026 Q1)

## Goal
Turn the archive's upstream **publication / authority / route-shaping seam** into a sharper **buildable program**.

The missing contribution is not a registry badge system, not a mandatory namespace regime, not a provenance engine that silently upgrades hints into proof, and not another policy dashboard.
It is a disciplined companion layer that lets Rust tools share **portable publisher/source identity truth** across package admission, trust review, distribution, support, incident response, and assistants without pretending those consumers all need the same power.

Read this note when the question is narrower than the broad ladder:

> if a serious Rust team decides to build the archive's clearest publication / authority / route-shaping seam, what should **Publisher & Source Identity** actually ship in theory and practice?

Read with:
- `design/publisher-source-identity-contract-2026Q1.md`
- `design/publisher-source-identity-stack.md`
- `design/package-intake-gateway-execution-blueprint-2026Q1.md`
- `design/distribution-contract-execution-blueprint-2026Q1.md`
- `design/worthy-contribution-shortlist-2026Q1.md`
- `proposals/epic-publisher-source-identity-stack.md`

## Why this note is needed now
The archive already knew that **Publisher & Source Identity Contract** was strategically real.
What it still lacked was a crisper answer to **what that contribution should actually look like**.

Fresh primary signals sharpen that answer:
- crates.io's January 2026 development update says Trusted Publishing now supports GitLab CI/CD in addition to GitHub Actions, crate owners can enforce **Trusted Publishing Only Mode**, risky `pull_request_target` and `workflow_run` triggers are blocked, and crate pages/index data now expose stronger public review inputs like SLOC and `pubtime`.
  https://blog.rust-lang.org/2026/01/21/crates-io-development-update/
- Cargo's publishing docs and `cargo owner` docs still distinguish **named owners** from **team owners**: named owners can add or remove owners, while team owners can publish or yank without owner-management powers.
  https://doc.rust-lang.org/cargo/reference/publishing.html
  https://doc.rust-lang.org/cargo/commands/cargo-owner.html
- Cargo's registry web API says Cargo itself does **not** have an inherent global notion of users and owners; registries decide how those are handled. That is a strong signal that Rust needs a portable handoff layer instead of pretending registry-local behavior is a universal built-in.
  https://doc.rust-lang.org/cargo/reference/registry-web-api.html
- Cargo's registry-authentication docs say authenticated alternate registries require a configured credential provider to avoid unknowingly storing unencrypted credentials on disk. That makes auth posture part of route identity, not just an implementation footnote.
  https://doc.rust-lang.org/cargo/reference/registry-authentication.html
- Cargo's registries and source-replacement docs keep **alternate registries** distinct from **exact-copy replacement sources**, and are explicit that replacement sources must contain exactly the same source code and may not add crates absent from the original source.
  https://doc.rust-lang.org/cargo/reference/registries.html
  https://doc.rust-lang.org/cargo/reference/source-replacement.html
- RFC 3243 and the active open-namespaces goal keep namespace-controlled families a live implementation seam, while RFC 3052 made `package.authors` optional and pushed crates.io/docs.rs toward current-owner presentation instead. That makes family claims, publish authority, and manifest authorship impossible to treat as one field any more.
  https://rust-lang.github.io/rfcs/3243-packages-as-optional-namespaces.html
  https://rust-lang.github.io/rust-project-goals/2025h2/open-namespaces.html
  https://rust-lang.github.io/rfcs/3052-optional-authors-field.html
- `cargo package` can emit `.cargo_vcs_info.json`, but the docs explicitly say it is a best-effort snapshot and that the package provenance is **not verified**. That is exactly the sort of useful but bounded source hint this seam should carry honestly.
  https://doc.rust-lang.org/cargo/commands/cargo-package.html
- The accepted verification-and-mirroring goal says Rust still lacks cryptographic security for the index, crates, and releases beyond HTTPS plus tamperable hashes in the index. That is a reminder that route identity and provenance security are adjacent, not already unified.
  https://rust-lang.github.io/rust-project-goals/2025h1/verification-and-mirroring.html

Taken together, those signals say the archive should stop describing Publisher & Source Identity only as a good boundary idea.
It should describe a real contribution shape.

## Headline answer
If one serious team wants to build the archive's clearest publication / authority / route-shaping contribution, the answer should now be:

> Build a **Publisher & Source Identity reference layer** that captures exact package subjects, imports claim/authority/route/hint lanes honestly, preserves provenance boundaries explicitly, and emits reusable packs and handoffs for intake, trust, distribution, support, incident, and assistant consumers.

That answer is deliberately narrower than “solve package trust”.
It is also deliberately stronger than “show more registry metadata”.

## What this contribution should be in theory

### Core thesis
A publisher/source-identity system becomes ecosystem infrastructure when it can answer all of these from one reviewable pack:
1. **what exact package or release subject is under discussion** — crate name/version, registry, package ID, workspace/release bundle identity where relevant;
2. **what claim lanes are being asserted** — namespace-controlled family, owner-curated family, maintainer-declared family, inferred family, or explicit non-claim;
3. **what publish-authority lanes applied** — named owner, team owner, trusted-publisher issuer, token-capable fallback, trusted-publishing-only posture, or unknown;
4. **what route/source semantics applied** — crates.io, alternate registry, local registry, vendored path, or exact-copy replacement source, plus auth/credential posture where relevant;
5. **what source hints exist and where provenance stops** — repository links, `.cargo_vcs_info.json`, package-side attachments, registry-verified facts, cryptographic proofs if any;
6. **what each downstream consumer is allowed to claim** from the resulting pack.

If a project cannot answer those questions without registry-specific lore, scattered Cargo config reading, and human memory, it is not yet the contribution the archive is pointing at.

### Boundary rule
The contribution should stop at **portable publisher/source identity and handoff**.

It should include:
- subject and route identity;
- claim-lane provenance;
- publish-authority posture;
- source-hint and provenance-boundary posture;
- bounded diffing and explanation;
- consumer-specific exports and handoffs.

It should not become:
- the new crates.io UI;
- a global trust score service;
- a namespace-governance platform;
- a universal provenance or signature system;
- or a policy engine that decides whether a crate is safe to use.

### Separation rule
The contribution must preserve at least six distinct truth classes:
- **subject truth** — what crate, version, registry, or package subject is being discussed;
- **claim truth** — what family/namespace/project relationship is asserted and on what basis;
- **publisher-authority truth** — who may publish and under which authority class;
- **source-route truth** — where the package came from and what route semantics/auth posture applied;
- **source-hint / provenance-boundary truth** — which attached facts are hints, which are registry-verified, and which are cryptographically verified;
- **consumer-handoff truth** — what a specific intake/trust/distribution/support/incident/assistant consumer may import.

This is the biggest theory/practice guardrail in the whole design.
Without it, every downstream consumer turns into a hidden fork of identity truth.

### Lane hierarchy rule
A worthy v0 should prefer identity lanes in this order:
1. **registry and Cargo-authoritative route/owner facts**;
2. **issuer-backed publishing posture and publish-mode facts**;
3. **namespace/family claim facts with explicit uncertainty**;
4. **package-side hint attachments**;
5. **verified provenance or mirroring attachments when present**;
6. **consumer-derived summaries**.

That order is strategic, not merely technical.
It keeps strongest currently-reviewable facts ahead of the highest temptation to over-claim trust or provenance.

## What this contribution should be in practice

### Reference tool shape
A serious v0 should probably look like a thin companion tool and schema family:
- `cargo source report`
- `cargo publisher report`
- `cargo source claim`
- `cargo source hints`
- `cargo source explain`
- `cargo source diff`
- `cargo source handoff --to <intake|trust|distribution|support|incident|assistant>`
- `cargo source pack`
- `cargo source doctor`

The tool should **import** Cargo/registry/service surfaces when available rather than replacing them.

### Public artifact spine
Keep the current family, but make the public review shape more explicit:
- `publisher-source-subject/v0`
- `claim-report/v0`
- `publisher-authority-report/v0`
- `source-route-report/v0`
- `source-hint-report/v0`
- `publisher-source-explanation/v0`
- `publisher-source-handoff/v0`
- `publisher-source-diff-report/v0`
- `publisher-source-pack/v0`

### Minimum schema disciplines
Every public artifact should keep these fields first-class:
- **subject identity** — crate/version/package ID/registry/source context;
- **authority posture** — named-owner, team-owner, issuer-backed trusted publisher, token-capable, trusted-publishing-only, or unknown;
- **claim posture** — namespace-controlled, owner-curated, maintainer-declared, inferred, explicit non-claim, or unresolved;
- **route posture** — crates.io, alternate registry, exact-copy replacement, local registry, vendored, or mixed;
- **provenance posture** — registry-verified fact, package-side hint, cryptographic proof, or none;
- **freshness / version anchors** — registry/API timestamps, `pubtime`, schema version, compared pack IDs, RFC/goal status where relevant;
- **consumer limits** — what the next consumer may and may not claim;
- **raw attachments** — owner lists, registry endpoints, config snippets, `.cargo_vcs_info.json`, repository URLs, or proofs when present;
- **reason-coded ambiguity** — explicit why for every partial, inferred, or unsupported answer.

### Commands and what they should emit

#### `cargo source report`
Purpose:
- gather route/source posture for one package subject;
- import registry, alternate-registry, replacement-source, vendored, or local-registry facts when available;
- emit `source-route-report/v0`.

Important rule:
- if the route is partly inferred from local config or install receipts, emit a visibly weaker report instead of pretending registry-authoritative identity.

#### `cargo publisher report`
Purpose:
- gather publish-authority posture;
- distinguish named owner, team owner, trusted-publisher issuer, and trusted-publishing-only posture;
- emit `publisher-authority-report/v0`.

Important rule:
- authority truth is not a trust verdict and should never silently widen into one.

#### `cargo source claim`
Purpose:
- capture project-family / namespace / curated-membership claims;
- distinguish namespace-controlled, owner-curated, maintainer-declared, inferred, and non-claim states;
- emit `claim-report/v0`.

Important rule:
- the absence of a namespace feature or family claim is a first-class outcome, not missing metadata to paper over.

#### `cargo source hints`
Purpose:
- import `.cargo_vcs_info.json`, repository links, package-side metadata, and other source hints;
- emit `source-hint-report/v0` with explicit provenance boundaries.

Important rule:
- one repository URL or VCS snapshot must never be rendered as verified provenance.

#### `cargo source explain`
Purpose:
- tell a human why an identity answer is authoritative, mixed, partial, inferred, or blocked;
- render the same pack at different depths without inventing new facts.

#### `cargo source diff`
Purpose:
- compare two packs while preserving the distinction between:
  - changed subject,
  - changed claim posture,
  - changed publisher authority,
  - changed route/source posture,
  - changed provenance-boundary posture,
  - and changed consumer claims.

#### `cargo source handoff`
Purpose:
- emit smaller consumer handoffs for package admission, trust review, distribution/install, support, incident response, or assistants without making those slices canonical by themselves.

#### `cargo source pack`
Purpose:
- bundle the current subject, claim, authority, route, hint, and handoff layers into one portable `publisher-source-pack/v0`.

#### `cargo source doctor`
Purpose:
- validate attachment presence, ambiguity posture, required consumer limits, and lossiness notes;
- tell maintainers when a pack is structurally incomplete rather than silently weak.

## What a good v0 should prove

### The proving lanes that actually matter
A worthy first version does **not** need to solve every governance dispute.
It needs to prove that one portable pack can survive real route and authority variety.

The first serious proving lanes should be:
1. **crates.io + named owner / team owner truth**;
2. **crates.io + trusted-publisher + trusted-publishing-only truth**;
3. **alternate registry + authenticated credential-provider posture**;
4. **source replacement / vendoring / local-registry route truth**;
5. **namespace-controlled or owner-curated family claim truth**;
6. **support / incident / package-admission consumer handoffs**.

### What the acceptance corpus should contain
A serious acceptance corpus should include fixtures for:
- a crate with named owners and team owners;
- a crate with trusted publishing enabled and token publishing blocked;
- a crate routed through an authenticated alternate registry;
- a crate using exact-copy source replacement;
- a vendored or local-registry scenario;
- a namespace-controlled family case and a merely inferred-prefix case;
- `.cargo_vcs_info.json` present but no verified provenance;
- a diff where publish authority changes but route does not;
- a diff where route changes but claim posture does not.

### `watch` / `defer` lanes
A disciplined v0 should explicitly mark these as `watch` / `defer` instead of faking completion:
- universal cryptographic provenance for every crate route;
- final crates.io namespace UX/governance decisions;
- full cross-registry owner-identity unification;
- arbitrary third-party “official project family” verification;
- complete install-path reconstruction when upstream identity was never captured.

## What adjacent layers should import, not replace
This contribution should become the thin identity source for:
- **Package Intake Gateway** when local ingress wants authority/route posture;
- **Trust Decision** when policy wants facts without re-deriving them;
- **Distribution Contract** when install/update/support needs upstream source identity;
- **Maintainer Reality / Keystone Stewardship** when support routing needs current ownership or issuer-backed posture;
- **incident and support packs** when people need to know how a package was sourced or who could publish it.

It should **not** try to absorb their downstream logic.

## Why this is strategically worthy
This seam matters because Rust's package story now has enough real identity surfaces that the bigger risk is **flattening them**:
- crates.io is surfacing more authority and publication posture;
- Cargo is clearer about alternate-registry and replacement-source differences;
- namespace/family control is live but incomplete;
- source hints are useful but not proof;
- and downstream consumers increasingly need one reviewable import instead of bespoke lore.

That combination is strong enough to justify a reference layer now.
It is not strong enough to justify pretending the ecosystem already has universal provenance or one canonical namespace regime.

## Recommended strategic rank
Treat this as the clearest current **publication / authority / route-shaping execution blueprint** in the archive.

It should sit:
- **below** the broad build-now leaders such as Build-State Evidence, Semantic Context, Migration/Public API, and Package Intake;
- **adjacent to** Distribution Contract, Trust Decision, and Support/Incident consumers;
- **upstream of** package-admission, install, support, and incident handoff tools;
- and **separate from** both final trust verdicts and final provenance systems.

## What not to build
Do **not** turn this into:
- a scalar trust score;
- a mandatory crates.io governance regime;
- a registry-only UI with no portable artifacts;
- a provenance theater layer that upgrades hints into proof;
- or a mega supply-chain suite that swallows package intake, trust policy, distribution, and support.

## Bottom line
If ideal Rust wants a worthy contribution around publication identity, the right answer is not “more badges” and not “wait until provenance is solved”.
It is a **Publisher & Source Identity reference layer** that makes claim truth, publish-authority truth, source-route truth, provenance boundaries, and bounded consumer handoffs reviewable enough that the rest of the ecosystem can stop reinventing them badly.
