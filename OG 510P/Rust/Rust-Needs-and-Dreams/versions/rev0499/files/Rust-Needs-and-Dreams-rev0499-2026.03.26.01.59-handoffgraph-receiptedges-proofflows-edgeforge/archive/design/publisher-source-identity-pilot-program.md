## Current interpretation after rev0446
This pilot program should now be read as the proving plan for `design/publisher-source-identity-execution-blueprint-2026Q1.md`.
The blueprint is the execution answer; this file is the ranked proof order.

# Design: Publisher & Source Identity pilot program

## Goal
Turn the archive’s org/source/publisher ideas into a ranked execution plan that can prove useful value before the ecosystem settles every long-running namespace or ownership debate.

## Why a pilot program is needed
This seam is easy to over-promise.
Rust does **not** yet have one settled global model for org identity, optional namespaces are still being implemented, and registry/source mechanics already have distinct semantics in Cargo.

So the right next move is a ranked pilot program that proves:
- source identity can be described honestly,
- publish authority can be exported portably,
- claim semantics can stay explicit and non-magical,
- and downstream trust/admission/install consumers can import those facts without reinterpreting them all differently.

## Pilot 1 — Source identity and auth posture
**Question:** Can we make registry/source configuration legible without changing Cargo’s core semantics?

Deliver:
- `source-report/v0` for crates.io, one alternate registry, and one source-replacement / mirror lane;
- clear distinction between `ALT_REGISTRY` and `SOURCE_REPLACEMENT`;
- auth posture fields and credential-provider detection;
- `cargo source verify` / `doctor` prototype.

Success means:
- a user can tell whether they are using a real alternate registry or an exact-copy replacement;
- an authenticated registry’s credential-provider posture is visible;
- no secrets are exposed.

## Pilot 2 — Publisher authority posture
**Question:** Can we report publish authority without silently turning it into trust policy?

Deliver:
- `publisher-report/v0` covering named-owner, team-owner, trusted-publisher issuer facts, and trusted-publishing-only mode where visible;
- explanation chains for why publishing is considered issuer-backed, token-capable, or team-mediated;
- explicit statement that owner/team/issuer posture is authority truth, not a trust verdict.

Success means:
- package-admission or trust consumers can import publisher posture cleanly;
- the report does not pretend that issuer-backed publishing alone is enough to trust the package.

## Pilot 3 — Claim / namespace posture
**Question:** Can Rust describe project-family claims before finalizing one universal namespace story?

Deliver:
- `claim-report/v0` for at least four classes:
  - maintainer-declared family claim,
  - namespace-controlled claim,
  - curated-source or registry-membership claim,
  - explicit uncertainty / non-claim;
- prototype import of optional-namespace status when available;
- compatibility with non-namespace org-family reporting and with owner-based UI surfaces.

Success means:
- users can see “project family” or “controlled namespace” facts without assuming all prefixed crates are equivalent;
- the pilot remains useful even if the final namespace rollout changes.

## Pilot 4 — Package-admission handoff
**Question:** Can publish review import identity truth without absorbing it into package policy?

Deliver:
- import `publisher-report/v0` and `source-report/v0` into a package-admission bundle;
- record package-vs-source authority facts separately from trust and policy decisions;
- add one proc-macro/build-lane example so authority posture is visible where scrutiny is often higher.

Success means:
- the package-admission bundle can answer both “what was admitted?” and “under what authority/source posture?”
- policy remains a consumer, not the owner of identity truth.

## Pilot 5 — Distribution/install consumer lane
**Question:** Can actual install receipts say enough about source and claim posture to help support and incident response?

Deliver:
- import selected identity fields into install receipts;
- distinguish source-built crates.io path, alternate-registry path, exact-copy mirror path, and curated/prebuilt source path;
- add incident/support examples showing why this matters after the fact.

Success means:
- later consumers can reconstruct how a tool reached a machine without over-claiming that publication identity settled installation truth.

## Explicit watch/wait boundaries
Do **not** require the pilot program to solve all of these before it is useful:
- final crates.io namespace UX,
- forced-transfer or ownership-governance policy,
- complete org verification across arbitrary domains,
- or universal signed-mirror infrastructure.

Those are adjacent questions, not prerequisites for proving the identity substrate.

## Boundary checks worth proving in the pilot
- A replacement source should never be rendered as merely “another registry”; the reports should preserve Cargo’s exact-copy semantics.
- Missing `package.authors` should not cause tools to silently label current owners or trusted-publisher subjects as authors.
- `.cargo_vcs_info.json` imports should remain visibly best-effort and unverified.
- Package-admission and install consumers should import identity facts with explicit lossiness notes instead of rewriting them as their own canonical truth.
