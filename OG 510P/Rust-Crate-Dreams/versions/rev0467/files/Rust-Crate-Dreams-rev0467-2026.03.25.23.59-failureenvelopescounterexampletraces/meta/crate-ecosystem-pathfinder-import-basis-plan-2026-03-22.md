# Crate ecosystem pathfinder — import-basis and visibility plan (2026-03-22)

This note sharpens **P-0509 Crate Ecosystem Pathfinder & Decision-Pack Kit** into a more operational next pass.

## Main judgment

A worthwhile next implementation pass should **not** spend most of its energy on ranking formulas.
It should add the boring review objects that explain **where candidate facts came from and what those facts do not prove**.

The missing value is the contract above today’s:

- crates.io pages,
- docs.rs pages and metadata,
- Cargo `search` / `add` / `info` commands,
- imported health and trust receipts,
- and maintainer-authored crate docs.

## What the crate should provide other people now

For maintainers, educators, platform teams, and downstream users, the crate should now provide:

1. **One candidate-basis receipt** instead of folklore about where the facts came from.
2. **One support-visibility report** instead of flattening docs.rs and registry surfaces into task fit.
3. **One portable pathfinder bundle** instead of a local ranking session that disappears after the meeting.
4. **One conservative distinction between declared, imported, inferred, and manual-review-only facts**.
5. **One bundle-level handoff** that another team can diff or reopen later without re-collecting every source.

## Three new first-class review objects

### 1. Candidate-basis receipt

`candidate-basis.receipt.json` should answer:

- which source surfaces were consulted for a candidate,
- what fact classes each surface supplied,
- what freshness and authority posture each fact has,
- and which important facts are still unresolved.

Recommended `0.2` fields:

- `candidate`
- `task`
- `source_inputs[]`
- `fact_classes[]`
- `inference_notes[]`
- `unresolved_questions[]`
- `manual_review_required`

### 2. Support-visibility report

`support-visibility.report.json` should answer:

- which public surfaces are visible to another user,
- whether the surface is registry, docs-hosted, Cargo-local, or imported evidence,
- what the surface appears to say,
- and what that surface still does **not** prove.

Recommended `0.2` visibility families:

- `registry_security_surface`
- `registry_publish_surface`
- `registry_size_surface`
- `docsrs_target_surface`
- `docsrs_feature_surface`
- `cargo_info_snapshot`
- `maintainer_authored_support_docs`

### 3. Pathfinder bundle manifest

`pathfinder-bundle.manifest.json` should answer:

- which task profile and decision pack belong together,
- which basis receipts and visibility reports back the decision,
- which starter-set lock and watch policies are in scope,
- and what a reviewer must import or resolve before trusting the packet.

## Recommended command surface additions

### `cargo pathfinder capture`
Capture public/imported candidate facts and emit:

- `candidate-import.report.json`
- `candidate-basis.receipt.json` (0 or more)
- `support-visibility.report.json` (0 or more)
- `evidence-origin.report.json`

### `cargo pathfinder bundle`
Emit one portable manifest joining:

- task profile,
- decision pack,
- starter-set lock,
- basis receipts,
- visibility reports,
- watch policies,
- and notes.

### `cargo pathfinder doctor`
Flag:

- basis gaps,
- visibility-vs-fit confusion,
- freshness ambiguity,
- or imported signals being over-read.

## Recommended proving grounds

- a task lane where `cargo add` finds a crate but does not prove it is the right starter-set pick;
- a candidate with a strong crates.io Security tab and Trusted Publishing posture but weak task fit;
- a candidate whose docs.rs default target or features create a persuasive public support story that still needs scope review;
- a portable bundle consumed by a second team that did not perform the original research.

## Design goals

1. **Basis before ranking** — explain what was observed before scoring it.
2. **Visibility is not fit** — public surface should help review, not collapse the decision.
3. **Portable reviewability** — another team should be able to inspect the packet later.
4. **Conservative inference** — inferred facts must stay labeled as inference.
5. **Import-aware humility** — imported health/trust/toolchain evidence should remain visibly imported.

## Non-goals

- not a replacement for crates.io search,
- not a total mirror of registry or docs.rs state,
- not a universal blessing engine,
- not a health or trust score engine,
- not an auto-migration planner.

## Artifact-completeness addendum

The lane now also needs three boring but receiver-critical artifacts:

- `candidate-basis.receipt.json` so source/basis lineage is portable;
- `support-visibility.report.json` so public surfaces can be reviewed without being mistaken for task fit;
- `pathfinder-bundle.manifest.json` so another team can receive one compact decision packet instead of a pile of half-remembered URLs.

These artifacts should remain conservative about what they prove.
A `cargo add` suggestion, a docs.rs landing target, a Security tab, SLOC, or `pubtime` are all useful facts.
None of them should silently become “best crate for the job”.
