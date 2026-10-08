# Design: Org Identity & Registry UX Kit (`cargo source`, `cargo publisher`, `publisher-report/v0`)

## Goal
Provide an adoption-ready **publisher/source identity substrate** for Rust tooling without forcing the ecosystem to settle every namespacing or ownership debate up front.

This kit should let Cargo-facing tools describe:
- **source identity** — which registry, mirror, or replacement source is in play;
- **publish authority** — who may publish and through which issuer/configuration;
- **project/org claims** — how a family of crates is presented or controlled;
- and the handoff into Trust, Policy, Package Admission, and Distribution consumers.

## Why this now looks worthy
The Rust ecosystem now has enough real ingredients that the missing layer is orchestration rather than aspiration:
- crates.io supports Trusted Publishing via OIDC and now supports GitLab CI/CD in addition to GitHub Actions, plus Trusted-Publishing-only mode;
- Cargo requires configured credential providers for authenticated alternative registries;
- Cargo keeps **registries** and **source replacement** as distinct mechanisms, and source replacement assumes exact-copy equivalence;
- RFC 3243 and the open-namespaces goal make namespace control an active implementation seam rather than a purely theoretical debate;
- current internals survey threads are explicitly trying to reduce circular debate around org ownership, alternative identifiers, and registry namespaces.

References:
- https://blog.rust-lang.org/2026/01/21/crates-io-development-update/
- https://doc.rust-lang.org/cargo/reference/registry-authentication.html
- https://doc.rust-lang.org/cargo/reference/registries.html
- https://doc.rust-lang.org/cargo/reference/source-replacement.html
- https://rust-lang.github.io/rfcs/3243-packages-as-optional-namespaces.html
- https://rust-lang.github.io/rust-project-goals/2025h2/open-namespaces.html
- https://internals.rust-lang.org/t/survey-of-organizational-ownership-and-registry-namespace-designs-for-cargo-and-crates-io/24027

## Core thesis
The kit should **not** pretend one concept covers all of these:
- human-readable project/org identity,
- owner lists,
- OIDC trusted-publisher subjects,
- namespace rights,
- alternate-registry configuration,
- exact-copy source replacement,
- and downstream policy verdicts.

Instead it should standardize small portable artifacts that keep those truths separate.

## Commands
### `cargo source`
Reference implementation can start as an external subcommand.

Core commands:
- `cargo source add <name> <index-or-source>`
  - adds alternate registries or managed source entries through a guided UX instead of raw config edits;
- `cargo source list`
- `cargo source verify <name>`
  - explains registry kind, sparse/git posture, auth requirements, credential-provider posture, and whether the source is a distinct registry or an exact-copy replacement;
- `cargo source doctor`
  - explains why Cargo resolved/authenticated a source the way it did;
- `cargo source report`
  - emits `source-report/v0`.

### `cargo publisher`
A second command family should focus on publish authority and claims.

Core commands:
- `cargo publisher report <crate-or-workspace>`
  - emits `publisher-report/v0` with owner / trusted-publisher / namespace posture;
- `cargo publisher claims <crate-or-prefix>`
  - emits `claim-report/v0` describing project/org claims, namespace-control posture, and explicit uncertainty or non-claims;
- `cargo publisher verify`
  - validates known issuers, owner posture, and available claim evidence without turning that into a trust verdict;
- `cargo publisher policy init`
  - scaffolds downstream policy imports without owning the policy layer.

Alias note: `cargo org` can remain a thin compatibility alias if the UX value is high, but `cargo publisher` better matches the real semantic boundary.

## Schemas
### `source-report/v0`
Purpose: capture **where packages are supposed to come from** and how Cargo is configured to authenticate or replace those sources.

Fields should include:
- source id / name / URL;
- source kind: `CRATES_IO`, `ALT_REGISTRY`, `SOURCE_REPLACEMENT`, `VENDORED`, `LOCAL_REGISTRY`, `LOCAL_DIRECTORY`;
- sparse/git posture;
- auth posture:
  - `AUTH_NOT_REQUIRED`
  - `AUTH_REQUIRED`
  - configured credential provider list / registry-specific provider presence;
- equivalence posture for replacements:
  - `EXACT_COPY_ASSUMED`
  - `NOT_A_REPLACEMENT_SOURCE`
- human label / homepage / notes;
- warnings / reason codes for misconfiguration.

### `publisher-report/v0`
Purpose: capture **who may publish** and how that authority is expressed.

Fields should include:
- package or workspace subject;
- current owners / owner classes when observable;
- trusted-publisher posture:
  - issuer kind (e.g. GitHub Actions, GitLab CI/CD),
  - subject constraints,
  - trusted-publishing-only mode when present;
- namespace-control posture when observable:
  - `NO_NAMESPACE_CONTROL`
  - `OPTIONAL_NAMESPACE_CONTROL`
  - `NAMESPACE_OPEN_TO_OTHERS`
  - `UNKNOWN`;
- supporting evidence links and freshness timestamps;
- warnings / reason codes.

### `claim-report/v0`
Purpose: capture **project/org claims** without silently equating them to publish authority.

Fields should include:
- claim subject (crate, prefix, namespace, source family, org label);
- claim type:
  - `PROJECT_FAMILY`
  - `ORG_OWNED`
  - `PUBLISHED_BY_TRUSTED_ISSUER`
  - `NAMESPACE_CONTROLLED`
  - `CURATED_SOURCE_MEMBERSHIP`;
- claim basis:
  - maintainer declaration,
  - registry fact,
  - namespace rule,
  - trusted-publisher config,
  - external curated mapping;
- explicit uncertainty / non-claim flags;
- links to publisher/source evidence.

### `publisher-source-pack/v0`
Attachable bundle containing the reports above for CI, package-admission review, trust imports, or install receipts.

## Integration points
### Trust Signals Kit
Import publisher/source facts as trust-relevant signals:
- publisher-control posture,
- issuer-backed publish evidence,
- source-family truth,
- namespace/name-risk context.

### Policy Kit
Consume publisher/source artifacts to express rules such as:
- allow only named registries/sources,
- require issuer-backed publishing for selected crates,
- treat namespace claims as informative only unless stronger authority exists.

### Package Admission Stack
Import publisher/source identity at publish time so a package-admission bundle can explain not just *what* was published, but *under which authority and source posture*.

### Distribution Contract Stack
Import source identity and claim evidence into install receipts so consumer-side tooling can distinguish:
- prebuilt fetched from source X,
- source-built from registry Y,
- exact-copy mirror path,
- or alternate-registry package path.

## Non-goals
- picking the final crates.io namespace policy for the ecosystem;
- replacing Trust Signals or Policy with an “identity verdict” engine;
- exposing secrets or tokens in reports;
- pretending source replacement, alternate registries, and namespaces are the same feature.

## Why this can become an epic contribution
A strong contribution here would not just be a nicer `cargo config` editor.
It would give Rust a portable answer to questions that recur across package admission, dependency selection, install receipts, trust review, and org governance:
- who controls this name or family,
- who actually may publish,
- where this package came from,
- and which claims are real facts versus merely helpful labels.
