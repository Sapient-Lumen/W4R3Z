# Pathfinder adjudication workbench plan — 2026-03-24

This note exists because **P-0509 Pathfinder** can no longer stop at comparison plus freeze.
A worthy first release now needs a small workbench for **adjudicating conflicting packet facts** and for **carrying a decision forward** without pretending the old packet never existed.

## Why this matters now

Current official substrate is finally rich enough to make this a real product surface:
- Cargo plumbing work breaks Cargo into programmatic phases rather than one giant opaque command.
- Cargo build analysis is explicitly about persisting machine-readable build metadata across invocations.
- `cargo metadata` is versioned and explicitly warns consumers to pin a format version.
- the registry index is intentionally close to immutable per version except `yanked`, but it still differs from `cargo metadata` and the Publish API.
- Cargo JSON message streams distinguish `compiler-artifact` and `build-script-executed` observations, and may surface cached build-script results even when the script did not rerun.
- docs.rs supports convenient `latest` and semver routes plus downloadable archives, but those still require explicit pinning and offline caveat handling.
- crates.io trust surfaces (`Trusted Publishing`, `Security` tab, `pubtime`, SLOC) help review, but they do not choose crates for you.

That is enough substrate for a real adjudication product.

## Product goal

The crate should help another team:
1. import two or more existing packets,
2. detect claim collisions and route differences,
3. review them in one compact workbench,
4. record the decision and its remaining manual zones,
5. and emit one carry-forward artifact that points to both the old packet and the new judgment.

## Receiver

Primary receivers:
- staff/principal engineer choosing or revalidating a starter set,
- maintainer reopening a frozen decision after a trigger,
- CI/policy tooling that must know whether a later judgment is inherited, superseded, or unresolved,
- and assistants/search surfaces that must not silently replace old basis with new convenience routes.

## First usable release shape

### Commands
- `cargo pathfinder adjudicate --from <packet-or-basis-lock>...`
- `cargo pathfinder carry-forward --session <adjudication-session.json>`
- `cargo pathfinder explain-conflict --claim <claim-id>`
- `cargo pathfinder export-notes --session <adjudication-session.json>`

A first release does **not** need a GUI.
A compact CLI + JSON + Markdown flow is enough.

### Core modules

#### 1. `packet-import`
Accepts:
- frozen decision packs,
- basis locks,
- knowledge packs,
- recheck tickets,
- transition packets,
- trusted public surfaces imported as receipts rather than crawled live.

#### 2. `claim-diff`
Builds one normalized conflict table showing:
- claim subject,
- source route,
- time basis,
- target/profile scope,
- policy scope,
- and whether the conflict is direct, partial, or only apparent.

#### 3. `adjudication-workbench`
Produces one `adjudication-session.report.json`.
This is the human-centered core.
It should record:
- imported packet refs,
- conflict list,
- weighting policy refs,
- chosen outcome for each conflict,
- unresolved items,
- and manual-review zones.

#### 4. `carry-forward`
Produces one `decision-carryforward.receipt.json`.
This should say:
- prior decision refs,
- adjudication-session ref,
- new decision ref,
- inherited claims,
- superseded claims,
- open deadlines / revisit triggers,
- and whether the carry-forward is full, partial, or temporary.

#### 5. `reopen-hook`
Optional in `0.1`, but the schema should already reserve space for:
- recheck deadline,
- trigger classes,
- next packet kind (`keep`, `revalidate`, `transition`, `manual_review`).

## What the crate should provide other people

For another team, the crate should provide:
1. one disagreement ledger small enough to review in minutes,
2. one adjudication session that preserves each conflicting route,
3. one carry-forward receipt that explains inheritance vs supersession,
4. one exportable Markdown decision note for humans,
5. one machine-usable state object for CI or later assistants,
6. and one visible list of ceilings where a human still has to decide.

That is much more useful than “just rerun the ranking” or “here is a refreshed summary”.

## First-release scenarios worth shipping

### Scenario A — docs.rs support story conflicts with task-fit policy
A candidate has stronger docs.rs visibility and Trusted Publishing posture, but still fails the local target/offline/native policy.
The workbench should record `better_public_posture != winner`.

### Scenario B — registry/index timing and docs.rs route both moved
A new release exists, `pubtime` changed, docs.rs `latest` moved, but no advisory exists.
The workbench should support `carry_forward_keep_with_recheck` rather than forced replacement.

### Scenario C — build observation conflict
A stored build-script result is cached while newer local observations differ.
The workbench should preserve observation mode instead of pretending both are the same fact.

### Scenario D — policy scope split
A teaching/default stack and a production/default stack are both legitimate.
The workbench should emit `split_scope` instead of forcing one global answer.

## Outcome vocabulary

Each conflict should end in one of:
- `keep_prior_claim`
- `accept_new_claim`
- `split_scope`
- `freeze_with_exception`
- `manual_review_required`
- `open_transition_review`

## Non-goals

This crate should **not** become:
- a general crawler,
- a hidden policy engine,
- a trust score service,
- an offline docs mirror,
- or a warehouse for every packet ever seen.

Those can exist around it.
The core value here is the **small adjudication session** and the **carry-forward receipt**.

## First usable release contract

A `0.1` counts as real if another team can:
1. import two conflicting packets,
2. see exactly which claims disagree,
3. record a reviewed outcome for each conflict,
4. emit a carry-forward receipt that preserves the old basis,
5. and reopen the same question later without inventing a fresh narrative.

If it cannot do that, it is still missing the product core.

## Sources

- https://rust-lang.github.io/rust-project-goals/2025h1/cargo-plumbing.html
- https://rust-lang.github.io/rust-project-goals/2025h2/cargo-build-analysis.html
- https://doc.rust-lang.org/cargo/commands/cargo-metadata.html
- https://doc.rust-lang.org/cargo/reference/external-tools.html
- https://doc.rust-lang.org/cargo/reference/registry-index.html
- https://docs.rs/about/rustdoc-json
- https://docs.rs/about/download
- https://blog.rust-lang.org/2026/01/21/crates-io-development-update/
- https://blog.rust-lang.org/2026/03/20/rust-challenges/
