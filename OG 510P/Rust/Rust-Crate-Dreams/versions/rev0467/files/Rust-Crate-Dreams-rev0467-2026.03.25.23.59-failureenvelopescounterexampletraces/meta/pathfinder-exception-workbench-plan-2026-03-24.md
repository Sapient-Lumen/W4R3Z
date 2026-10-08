# Pathfinder exception workbench plan — 2026-03-24

This note exists because **P-0509 Pathfinder** can no longer stop at comparison, freeze, adjudication, and carry-forward.
A worthy first release now needs a small workbench for **bounded exceptions**: temporary relief that is visible, scoped, owned, evidence-linked, and expiring.

## Why this matters now

Current Rust tooling already exposes several local escape hatches, but they are fragmented:
- Cargo Vet can initialize projects by adding `exemptions`, can regenerate them, can mark packages exempted from review, and explicitly describes exemptions as backlog that should usually shrink over time.
- Cargo Vet also has trusted entries and wildcard audits with end dates plus a `renew` command for expirations.
- cargo-deny can ignore advisories with an explicit reason and can define per-crate license exceptions.
- cargo-semver-checks is aiming for a publish-time override path while also generating witness programs showing how downstream code could break.
- crates.io and docs.rs expose enough public posture and timing metadata to anchor exception decisions in visible evidence rather than folklore.
- safety-critical guidance says higher-integrity teams often internalize, wrap, or replace dependencies later, which means temporary exception handling is part of serious Rust adoption.

That is enough substrate for a real exception product.

## Product goal

The crate should help another team:
1. import a frozen decision or adjudication outcome,
2. record a narrow exception instead of silently overriding the recommendation,
3. bind that exception to owner, scope, evidence, and expiry,
4. emit one portable receipt for humans and tools,
5. and open one expiry ticket when the exception must be renewed, removed, or turned into a transition.

## Receiver

Primary receivers:
- staff/principal engineer accepting a bounded policy gap to keep delivery moving,
- maintainer using Cargo Vet, cargo-deny, or docs/build evidence but wanting one cross-tool review packet,
- policy/compliance/CI tooling that must know whether a risk is accepted, for how long, and by whom,
- and assistants/search surfaces that must not retell a temporary exception as if it were general support truth.

## First usable release shape

### Commands
- `cargo pathfinder except --from <decision-or-adjudication-ref> --kind <kind>`
- `cargo pathfinder expire --exception <policy-exception.receipt.json>`
- `cargo pathfinder budget --from <packet-dir>`
- `cargo pathfinder export-exception-note --exception <policy-exception.receipt.json>`

A first release does **not** need deep workflow automation.
A compact CLI + JSON + Markdown flow is enough.

### Core modules

#### 1. `exception-intake`
Accepts:
- frozen decision packs,
- adjudication sessions,
- carry-forward receipts,
- revalidation packets,
- and imported tool-specific artifacts such as Cargo Vet exemptions/trust or cargo-deny ignore entries as evidence rather than authority.

#### 2. `scope-and-owner`
For every exception, records:
- subject crate(s),
- task/profile/target scope,
- owner,
- approval authority,
- and whether the exception applies to `dev_only`, `test_only`, `production`, `air_gapped`, `regulated`, or another explicit scope.

#### 3. `evidence-and-witness-linker`
Links the exception to:
- basis locks,
- imported public-surface receipts,
- Cargo Vet or cargo-deny evidence,
- semver-check witnesses where available,
- and local notes explaining what was checked and what still was not.

#### 4. `expiry-and-trigger`
Produces one `exception-expiry.ticket.json` saying:
- expiry date,
- renewal conditions,
- removal path,
- follow-up trigger classes,
- and whether the next packet should be `renew`, `remove`, `revalidate`, or `transition`.

#### 5. `budget-summary`
Optional for `0.1`, but the schema should reserve space for:
- active exception count,
- grouped exceptions by owner/scope,
- oldest expiry,
- and which exceptions lack witnesses or removal paths.

## What the crate should provide other people

For another team, the crate should provide:
1. one exception receipt small enough to review in minutes,
2. one visible scope/owner/authority record,
3. one evidence list showing why the exception exists,
4. one expiry ticket that prevents exception amnesia,
5. one Markdown note suitable for design review or compliance review,
6. and one machine-usable state object for CI or later assistants.

That is much more useful than “just ignore this for now” or “we have an exemption somewhere in config”.

## First-release scenarios worth shipping

### Scenario A — Cargo Vet exemption plus cargo-deny ignore
A dependency is accepted temporarily because audit backlog is still open and one advisory is being ignored under a scoped exception.
The workbench should keep those as imported evidence and emit one local exception packet with owner, reason, scope, and expiry.

### Scenario B — semver witness says breakage is real but local release must proceed
A maintainer decides to ship with an override while planning a major release or follow-up repair.
The workbench should preserve the witness and record that the exception is release-scoped, not ecosystem-wide truth.

### Scenario C — docs.rs public support is partial because of sandbox/resource limits
A crate is still chosen for a local target, but public docs posture remains partial.
The workbench should support `keep_with_docs_exception` rather than rewriting the support story.

### Scenario D — safety-critical narrowing path
A team uses a dependency at low criticality today but plans to wrap or replace it before moving up the assurance ladder.
The workbench should emit `temporary_use_with_internalization_plan` rather than pretending the dependency is cleared forever.

## Outcome vocabulary

Each exception should end in one of:
- `temporary_keep`
- `scope_limited_allow`
- `keep_with_followup_witness`
- `open_transition_review`
- `manual_review_required`

## Non-goals

This crate should **not** become:
- a generic policy engine,
- an auto-generator of ignore files,
- a supply-chain scanner,
- a waiver silo disconnected from evidence,
- or a tool that erases the distinction between exception and support.

Those can exist around it.
The core value here is the **small exception receipt** and the **expiry ticket**.

## First usable release contract

A `0.1` counts as real if another team can:
1. import a frozen decision or adjudication packet,
2. record a narrow exception with owner, scope, evidence, and expiry,
3. emit one portable receipt and one expiry ticket,
4. show a reviewer what removes that exception later,
5. and reopen the same question without inventing a fresh narrative.

If it cannot do that, it is still missing the product core.

## Sources

- https://mozilla.github.io/cargo-vet/commands.html
- https://mozilla.github.io/cargo-vet/performing-audits.html
- https://embarkstudios.github.io/cargo-deny/cli/init.html
- https://rust-lang.github.io/rust-project-goals/2025h2/cargo-semver-checks.html
- https://docs.rs/cargo-semver-checks/latest/cargo_semver_checks/
- https://blog.rust-lang.org/2026/01/21/crates-io-development-update/
- https://docs.rs/about/builds
- https://docs.rs/about/metadata
- https://blog.rust-lang.org/2026/01/14/what-does-it-take-to-ship-rust-in-safety-critical/
- https://blog.rust-lang.org/2026/03/20/rust-challenges/
