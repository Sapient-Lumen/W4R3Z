## 2026Q1 promotion note
Read this stack now as the substrate beneath [`design/migration-truth-contract-2026Q1.md`](./migration-truth-contract-2026Q1.md).
The stack still matters because it explains leaf ownership and execution order, but the repo now treats the missing contribution as a first-class **Migration Truth Contract** rather than a floating collection of upgrade aids.

# Design: Migration Truth Stack (Migration + Edit Workflow + Public API + Support Envelope + DocProof + Downstream Testing)

## Goal
Treat **Migration Kit** as the orchestration layer in a broader **Migration Truth Stack**.

The missing contribution is not another upgrader, another fixer wrapper, another dependency-bump bot, or another release checklist.
It is a portable, reviewable stack that keeps six distinct truths separate while letting them compose:
- **source-state truth** — what edition, toolchain, `rust-version`, dependency posture, support envelope, and docs/release assumptions the subject started from;
- **destination-intent truth** — what state the project is trying to reach, with what compatibility posture and approval rules;
- **mechanical-edit truth** — which candidate edits were suggested, selected, applied, rejected, or deferred;
- **compatibility truth** — what public API, support, docs, and downstream consequences were actually checked;
- **run/outcome truth** — what the migration run actually exercised, what remained partial, and what final claim is now supported;
- **release-consumer truth** — what policy, release, support, downstream packagers, and later maintainers may now safely conclude.

That separation matters because Rust migrations are rarely a single lane:
- edition upgrades involve compiler suggestions plus manual semantics review;
- dependency upgrades involve lock movement, feature/control policy, and API consequences;
- toolchain/MSRV ratchets involve workspace policy, verification scope, and support changes;
- docs, examples, and downstream consumers can break even when the code compiles;
- and release claims often lag behind what the migration tools happened to edit.

## Why this seam matters now
Current Rust signals are unusually aligned around the need for a real migration program layer:
- The Edition Guide explicitly frames advanced edition migration as a staged workflow rather than one command, and Cargo documents `cargo fix` as configuration-sensitive and partial.
  https://doc.rust-lang.org/edition-guide/editions/advanced-migrations.html
  https://doc.rust-lang.org/cargo/commands/cargo-fix.html
- Rust 1.85 / Rust 2024 says `cargo fix` output is intentionally conservative and should not be treated as a recommendation. That is direct evidence that applied edits and intended semantics must stay distinct.
  https://blog.rust-lang.org/2025/02/20/Rust-1.85.0/
- Cargo’s 1.90 cycle and the 2025 GSoC results both say the current `cargo fix` architecture is slow, incomplete, and awkward for selective or interactive flows. That means the ecosystem should design the evidence/orchestration layer above whichever edit engine wins.
  https://blog.rust-lang.org/inside-rust/2025/10/01/this-development-cycle-in-cargo-1.90/
  https://blog.rust-lang.org/2025/11/18/gsoc-2025-results/
- Cargo’s `rust-version` docs say workspace verification gets complicated when policies differ, and rustup already makes committed toolchain selection first-class.
  https://doc.rust-lang.org/cargo/reference/rust-version.html
  https://rust-lang.github.io/rustup/overrides.html
- The public-API direction remains active: public/private dependencies and `cargo-semver-checks` are explicitly on the path toward stronger publish-time compatibility review, while docs.rs now hosts rustdoc JSON for machine-usable docs evidence.
  https://rust-lang.github.io/rust-project-goals/2026/flagships.html
  https://rust-lang.github.io/rust-project-goals/2025h1/pub-priv.html
  https://rust-lang.github.io/rust-project-goals/2025h2/cargo-semver-checks.html
  https://docs.rs/about/rustdoc-json

Taken together, ideal Rust needs a migration substrate that is broader than edit application but narrower than “one mega release platform”.

## What each kit should own
### Migration Kit
[`design/migration-kit.md`](./migration-kit.md) owns:
- source state,
- destination intent,
- preflight analysis imports,
- ordered plans,
- run receipts,
- final outcome claims,
- optional waivers.

Its question is:
> what transition is this subject trying to make, and what final claim can it now honestly support?

### Edit Workflow Kit
[`design/edit-workflow-kit.md`](./edit-workflow-kit.md) owns:
- candidate edit capture,
- selection plans,
- application receipts,
- verification of tree mutations.

Its question is:
> what mechanical code/config/doc changes were proposed, approved, and applied?

### Public API Kit
[`design/public-api-kit.md`](./public-api-kit.md) owns:
- export/provenance drift,
- semver reason codes,
- dependency exposure posture,
- witness-based compatibility evidence.

Its question is:
> what release-boundary/API consequences did this transition create?

### Support Envelope Kit
[`design/support-envelope-kit.md`](./support-envelope-kit.md) owns:
- dev-host/source-build/release-artifact/docs/runtime-floor claims,
- observed support evidence,
- support diff reports.

Its question is:
> what support contract changed, and how well was it verified?

### DocProof Kit
[`design/docproof-kit.md`](./docproof-kit.md) owns:
- guide/API/transcript/example validation,
- docs.rs assumptions,
- illustrative-vs-checked teaching material.

Its question is:
> what documentation/learning surfaces remained true after the transition?

### Downstream Testing Kit
[`design/downstream-testing-kit.md`](./downstream-testing-kit.md) owns:
- consumer suites,
- selected downstream sets,
- observed breakage or compatibility evidence.

Its question is:
> what happened in the real consumer world beyond the local crate or workspace?

## Shared stack thesis
A worthy contribution here should let a reviewer answer all of these without reconstructing the truth from CI YAML, command transcripts, issue comments, branch naming, and maintainer memory:
1. What was the exact source state and intended destination?
2. Which configuration slices and package subsets were actually in scope?
3. Which edits were conservative tool output versus deliberate migration choices?
4. Which compatibility/support/docs/downstream lanes were actually checked?
5. Which claims were accepted with waivers or left partial/inconclusive?
6. What release/support/policy consumers may now safely import?

If the stack cannot answer those six questions, it is not yet ecosystem infrastructure.

## Recommended execution posture
The stack now needs a ranked execution layer, captured in:
- [`design/migration-pilot-program.md`](./migration-pilot-program.md)
- [`proposals/epic-migration-truth-stack.md`](../proposals/epic-migration-truth-stack.md)

The pilot program is the rollout discipline.
The new epic is the explicit stack-level product target: a thin `cargo migrate` / `migration-pack/v0` layer above Migration Kit plus imported Edit Workflow, Public API, Support Envelope, DocProof, and Downstream Testing evidence.

That pilot program should prove the stack in this order:
1. **edition transition lane**
2. **workspace toolchain / `rust-version` lane**
3. **dependency-upgrade + API/MSRV lane**
4. **docs/support/downstream lane**
5. **release / archaeology / migration-diff lane**

That ordering is intentional.
The archive should not jump straight to one universal upgrade bot, one giant migration dashboard, or a fake “upgrade health” score.
It should first prove that Rust projects can publish enough migration truth to make ordinary compatibility-sensitive changes reviewable.

## Design principles
1. **Source and destination states come before automation.** Reviewable migration starts from explicit baselines and explicit goals.
2. **Mechanical edits are not the migration.** `cargo fix`, manifest updates, and lockfile changes are evidence inside a broader transition program.
3. **Compatibility consumers stay imports, not absorbed subfields.** API, support, docs, downstream, and release lanes must keep their own artifacts.
4. **Partial completion must be explicit.** A migration can be valuable while still incomplete, but only if the incompleteness is preserved honestly.
5. **One stack, many consumers.** Policy, release, support, downstream, and future atlas/semantic tooling should all be able to import the same migration outcome.
6. **The stack should survive time.** A migration pack should still explain itself months later when the original CI logs, chat context, and branch discipline are gone.

## What an epic contribution would look like in practice
The stack-level direction is now explicit in [`proposals/epic-migration-truth-stack.md`](../proposals/epic-migration-truth-stack.md).
A serious contribution here would:
- attach ordered migration programs to ordinary PR/release review;
- preserve the difference between conservative edits and intentional destination semantics;
- make edition, dependency, MSRV, support, docs, and downstream changes speak about the same transition subject;
- let release notes, support pages, and policy tools cite structured migration outcomes instead of maintainer lore;
- and create a durable archaeology surface for future maintainers.

## Anti-goals
Do not turn this stack into:
- one magic universal upgrader,
- one more dependency-bump bot with nicer marketing,
- one giant release-management platform,
- or one fake migration score.

The stack is a **review boundary**, not a replacement for all migration tooling.
