# Design: Edit Governance Pilot Program

## Why this needs its own pilot layer
The archive already argues that Rust needs a reviewable edit boundary. What it still lacked was a ranked answer to **how that boundary should enter real workflows without bypassing review**.

That rollout matters because current Rust signals are converging:
- Cargo’s current `cargo fix` architecture is acknowledged as slow, selective only in awkward ways, and hard to make interactive because it relies on a `rustc`-proxy mode with locking.
  https://blog.rust-lang.org/inside-rust/2025/10/01/this-development-cycle-in-cargo-1.90/
- The `cargo-fixit` prototype moves control back to the top-level program and opens the door to coordination and interactive selection.
  https://blog.rust-lang.org/2025/11/18/gsoc-2025-results/
- Cargo’s structured logging / `cargo report` work is explicitly considering schema unification with Cargo JSON output because that could unblock a faster, more flexible `cargo fix` architecture.
  https://blog.rust-lang.org/inside-rust/2026/01/07/this-development-cycle-in-cargo-1.93/
- Rust’s 2025 survey says online docs remain the canonical reference while LLM tooling and agentic/editor workflows are rising.
  https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- docs.rs now hosts rustdoc JSON with explicit `format_version` handling, and StableMIR is being positioned as a stable tool-facing compiler interface.
  https://docs.rs/about/rustdoc-json
  https://rust-lang.github.io/rust-project-goals/2025h1/stable-mir.html

That combination means a worthy contribution is no longer “another refactor tool”. It is a **governed execution layer** that keeps canonical Rust knowledge, candidate edits, selection, application, and verification separate.

## Pilot principles
1. **Canonical facts first.**
   - Semantic inputs from Cargo, rustdoc JSON, compiler exports, and diagnostics stay canonical.
   - Assistant/editor renderings are downstream consumers, not replacement truth.

2. **Candidate generation is not approval.**
   - Producers may emit candidates freely.
   - Nothing becomes an approved change without an explicit selection plan.

3. **Application is not verification.**
   - A patch landing on disk is not the same as the code being accepted.

4. **Assistant lanes come late and weak.**
   - Assistant-generated patches should enter as low-authority candidate bundles, not direct working-tree mutation.

5. **Staleness must be first-class.**
   - Candidate spans, AST paths, and semantic assumptions can drift quickly; “stale against current subject” is a normal result.

## Required artifact spine
Every serious pilot should require, at minimum:
- `edit-subject/v0`
- `edit-candidate-report/v0`
- optional `semctx-pack/v0` or `semantic-query-report/v0` reference when semantic context matters
- `edit-selection-plan/v0` before any apply lane
- `edit-apply-report/v0` when changes touch disk
- `edit-verify-report/v0` before a pilot claims success

Design rule: **no pilot should skip straight from producer output to “done”.**

## Ranked pilots

### 1. Compiler suggestion export / selection lane
**Why first**
- `rustc` already emits structured diagnostics with suggestions and applicability metadata.
- `cargo fix` already proves that compiler-suggestion application is a mainstream workflow.
- This is the narrowest credible lane for establishing the artifact family.

**Scope**
- Collect compiler suggestions into `edit-candidate-report/v0`
- Preserve diagnostic id, span, applicability, and lint/error-code provenance
- Support explicit selection by lint, package, target, or applicability class
- Emit preview and apply receipts without needing assistant or IDE integration

**Success condition**
- A maintainer can review “all machine-applicable suggestions for package X under feature set Y” as an attachable plan instead of as a hidden `cargo fix` run.

### 2. Cargo fix / edition migration lane
**Why second**
- Edition migration is where Rust already admits that fix workflows can require partial, repeated, and manual steps.
- This lane forces the kit to represent ordered waves, partial migration, `--broken-code`, and target/feature-specific runs honestly.

**Scope**
- Support edition/idiom migration plans as phased waves
- Preserve which lints or migration groups were active
- Preserve broken-but-kept states and manual follow-up markers
- Attach verification scope (`cargo check`, `cargo test`, docs, selected targets/features)

**Success condition**
- An edition migration can be replayed and reviewed as candidate → plan → apply → verify rather than reconstructed from terminal logs and human memory.

### 3. rust-analyzer assist / SSR export lane
**Why third**
- rust-analyzer already spans assists, diagnostic fixes, rename/refactor commands, and SSR-like workflows, but editor sessions are still an awkward review boundary.
- This is the first lane that proves the kit is not Cargo-only.

**Scope**
- Export selected assists / SSR runs / rename batches as candidates
- Preserve producer identity, editor/session origin, and quality-affecting settings where relevant
- Keep editor-only conveniences distinct from Cargo-native truth
- Require the same explicit selection / preview / apply / verify path as Cargo-originated edits

**Success condition**
- A useful refactor can leave the editor as an attachable review artifact instead of only as an ephemeral local action.

### 4. Assistant proposal lane
**Why fourth**
- The survey signal says these tools are rising, but they should enter only after the archive has already proven canonical-first lanes.
- This is where governance matters most.

**Scope**
- Assistant outputs must arrive as `assistant proposal` candidates with explicit weaker authority
- Require an imported semantic-context reference or mark the proposal as context-poor
- Default policy should forbid direct apply
- Require stronger verification and manual approval posture than compiler or known-refactor lanes

**Success condition**
- Assistant suggestions become inspectable and comparable without being allowed to masquerade as compiler facts or trusted editor refactors.

### 5. CI / review-bot consumer lane
**Why fifth**
- Only after the earlier lanes work should CI or bots begin aggregating or enforcing policy.
- This lane proves the artifacts are stable enough for non-interactive consumers.

**Scope**
- CI imports packs, runs policy over them, and links verification/report artifacts
- Preserve advisory versus blocking outcomes
- Support policy such as “machine-applicable compiler fixes may auto-queue preview packs, assistant proposals may not”
- Never let CI rewrite the branch without a recorded plan/apply/verify chain

**Success condition**
- Review automation consumes edit packs without turning them into silent branch mutation.

## What not to do
- Do **not** start with assistant-generated bulk patches.
- Do **not** collapse semantic context capture into edit artifacts.
- Do **not** treat rust-analyzer or assistants as canonical truth sources.
- Do **not** require one universal edit engine before piloting export/review/apply boundaries.
- Do **not** flatten all producers into one confidence level.

## Graduation criteria
A pilot should only graduate when it can show:
1. explicit subject identity;
2. candidate provenance and conflict truth;
3. a visible selection plan;
4. an application receipt;
5. attached verification evidence;
6. honest stale/incomplete outcomes;
7. at least one downstream consumer besides the original producer.

## Archive posture
This pilot program is the missing execution layer between:
- [`design/semantic-context-kit.md`](./semantic-context-kit.md), which owns canonical machine-usable context;
- [`design/edit-workflow-kit.md`](./edit-workflow-kit.md), which owns edit artifacts and governance;
- and future Cargo / rust-analyzer / assistant consumers that should **compose through those boundaries** instead of bypassing them.
