# Design: Migration pilot program (`cargo migrate pilot`, `migration-pack/v0`)

## Goal
Make the archive treat **Migration Kit** as a real execution program rather than a good-but-floating design.

The missing contribution is not merely “better upgrades”.
It is a disciplined rollout that proves Rust projects can publish **portable migration evidence** for a few high-value lanes before widening scope.

## References (signals)
- The Edition Guide’s advanced migration path is explicitly staged and configuration-sensitive.
  https://doc.rust-lang.org/edition-guide/editions/advanced-migrations.html
- Cargo documents `cargo fix` as applying compiler suggestions, with scope controlled by package/target/feature/profile selection.
  https://doc.rust-lang.org/cargo/commands/cargo-fix.html
- Rust 1.85 / Rust 2024 says `cargo fix` output is conservative and should not be taken as a recommendation.
  https://blog.rust-lang.org/2025/02/20/Rust-1.85.0/
- Cargo’s 1.90 development cycle says the current `cargo fix` architecture makes selectivity and interaction hard, and the 2025 GSoC results confirm active work on alternative architecture.
  https://blog.rust-lang.org/inside-rust/2025/10/01/this-development-cycle-in-cargo-1.90/
  https://blog.rust-lang.org/2025/11/18/gsoc-2025-results/
- Cargo’s `rust-version` docs say workspaces can have multiple policies and that verification can get complicated.
  https://doc.rust-lang.org/cargo/reference/rust-version.html
- rustup already makes committed toolchain selection and overrides explicit.
  https://rust-lang.github.io/rustup/overrides.html
- Public/private dependencies and `cargo-semver-checks` remain active supply-chain / publish-path work, which means API-sensitive migration evidence now has a credible downstream consumer.
  https://rust-lang.github.io/rust-project-goals/2026/flagships.html
  https://rust-lang.github.io/rust-project-goals/2025h1/pub-priv.html
  https://rust-lang.github.io/rust-project-goals/2025h2/cargo-semver-checks.html
- docs.rs now hosts rustdoc JSON, which makes attachable docs/API evidence more practical during migrations.
  https://docs.rs/about/rustdoc-json

## Why this needs its own design layer
Without a shared pilot program, migration work is vulnerable to three bad outcomes:
1. **fix theater** — lots of auto-edits, little durable truth about destination semantics;
2. **upgrade theater** — dependency/toolchain movement with weak scope/evidence boundaries;
3. **release theater** — support/API/docs/downstream claims asserted from green CI alone.

A ranked pilot program is how the archive proves that migration truth can stay compact, reviewable, and honest.

## Design principles
1. **Start from explicit subjects.** The pilot should always begin with a clear source state and intended destination.
2. **Keep imported evidence distinct.** Edit, API, support, docs, and downstream packs must remain attachments, not collapsed fields.
3. **Treat partial success as a real outcome.** Incomplete migrations should emit useful outcome reports instead of disappearing into local TODOs.
4. **Prefer ordinary maintainer flows first.** The first pilots should attach to PR/release review before any speculative automation.
5. **Make archaeology a first-class success bar.** Months later, a maintainer should still be able to tell what happened and what remains deferred.

## Shared pilot artifacts
### `migration-brief/v0`
A short declaration of why a lane is being piloted.

Should record:
- pilot id
- lane family (`edition`, `toolchain-msrv`, `dependency-api`, `docs-support-downstream`, `release-archaeology`)
- why this lane matters
- selected subject types
- intended consumers and success bar

### Core imports from Migration Kit
- `migration-subject/v0`
- `migration-intent/v0`
- optional `migration-analysis-report/v0`
- `migration-plan/v0`
- optional `migration-run-report/v0`
- optional `migration-outcome-report/v0`
- optional `migration-waiver/v0`

### Expected attachments from other kits
- optional `edit-pack/v0`
- optional `api-pack/v0`
- optional `support-pack/v0`
- optional `doc-pack/v0`
- optional downstream test attachments
- optional release manifest / release-policy attachments

### `migration-pilot-pack/v0`
Portable bundle for a specific migration pilot lane.

Should contain:
- the pilot brief
- one migration subject + intent pair
- the selected plan/run/outcome artifacts
- imported edit/API/support/docs/downstream attachments where relevant
- explicit partial/inconclusive markers
- review summary and unresolved follow-up items

Design rule: **this pack is a composition envelope, not a mega-schema that absorbs the underlying kits.**

## Ranked rollout

### Pilot 1 — Edition transition truth
Start with the most canonical, best-documented migration lane.

Suggested subject:
- one crate moving from edition 2021 to 2024 with explicit feature/target/profile scope

Artifacts:
- `migration-subject/v0`
- `migration-intent/v0`
- `migration-analysis-report/v0`
- `migration-plan/v0`
- `migration-run-report/v0`
- optional `edit-pack/v0`
- optional `doc-pack/v0`
- `migration-outcome-report/v0`

Success bar:
- the archive can preserve conservative fixes versus intentional semantic decisions;
- configuration slices actually exercised are explicit;
- residual manual blockers are reason-coded rather than hidden in review comments.

### Pilot 2 — Workspace toolchain / `rust-version` ratchet
Once edition truth is working, prove that migration artifacts can handle policy-heavy workspace change.

Suggested subject:
- one workspace ratcheting `rust-version` and/or `rust-toolchain.toml` with package-specific verification

Artifacts:
- migration subject/intent/plan/run/outcome
- `support-pack/v0` attachment where support posture changes
- explicit package/target split markers
- optional waiver for packages or targets left deferred

Success bar:
- package-specific verification is preserved;
- workspace-wide versus package-local toolchain consequences are explicit;
- support/runtime-floor implications do not get hidden inside toolchain files.

### Pilot 3 — Dependency upgrade + API/MSRV lane
Next, prove that dependency-sensitive transitions can import compatibility evidence without collapsing into it.

Suggested subject:
- one library crate taking a major dependency upgrade or public/private-boundary change

Artifacts:
- migration subject/intent/analysis/plan/run/outcome
- `api-pack/v0`
- optional dependency-control imports
- optional MSRV/toolchain evidence

Success bar:
- dependency movement, API consequences, and destination acceptance are all visible but distinct;
- false certainty is avoided when analysis remains partial;
- release-relevant compatibility conclusions are attachable.

### Pilot 4 — Docs / support / downstream lane
Only after source/destination and compatibility evidence are stable should the pilot widen to user-facing claims.

Suggested subject:
- one migration that changes support posture, docs assumptions, or important downstream consumers

Artifacts:
- migration plan/run/outcome
- `doc-pack/v0`
- `support-pack/v0`
- downstream testing attachments
- optional waiver for deferred docs/support/downstream work

Success bar:
- docs breakage, support drift, and downstream fallout can attach to the same migration subject;
- release-facing user claims no longer depend on green local compilation alone.

### Pilot 5 — Release / archaeology / migration-diff lane
Widen last, once the migration boundary is already useful to maintainers.

Suggested subject:
- compare two migration outcomes or one attempted migration versus the accepted result

Artifacts:
- two `migration-pack/v0` baselines or one pack plus a diff view
- linked release/support notes
- optional policy/release attachments

Success bar:
- a later maintainer can tell what changed, what was waived, and what final claim was actually adopted;
- the migration pack is useful after ephemeral CI/chat context is gone.

## What should count as success overall
The pilot program is working when:
- edition and toolchain transitions can be reviewed as explicit programs rather than command transcripts,
- dependency/API-sensitive migrations can import compatibility evidence without flattening it,
- docs/support/downstream claims attach to the same transition subject,
- partial or inconclusive migrations stay useful instead of disappearing,
- and future maintainers can audit the final claim months later.

## Failure modes to avoid
- Starting with one universal upgrade bot.
- Treating `cargo fix` output as the migration’s final semantics.
- Hiding support or downstream drift behind successful compilation.
- Flattening imported attachments into one fake migration score.
- Waiting for Cargo core to absorb everything before proving the artifact boundary.

## Immediate archive instruction
Treat this file plus [`design/migration-truth-stack.md`](./migration-truth-stack.md) and [`proposals/epic-migration-truth-stack.md`](../proposals/epic-migration-truth-stack.md) as the shared execution layer above Migration Kit.

The next credible migration move is now a ranked stack program:
1. edition transition truth,
2. workspace toolchain / `rust-version` truth,
3. dependency-upgrade + API/MSRV truth,
4. docs/support/downstream truth,
5. release / archaeology / migration-diff truth.
