## Current framing (rev0402)
The archive should now read this file through `design/semantic-context-contract-2026Q1.md`.

Interpretation rule:
- **Semantic Context Kit** owns the portable substrate for **subject identity + authority lane + merge/completeness + query/result + comparison/handoff** truth;
- keep it explicitly distinct from **Compiler Extensibility Stack** (attachment/result-family discipline) and **Reviewable Edit Contract** (candidate/apply/verify mutation discipline);
- do not let one docs.rs cache, one local rustdoc JSON build, one `cargo metadata` walk, one `rmeta` merge, or one assistant slice impersonate the whole semantic answer.


# Design: Semantic Context Kit (`cargo semctx`, `semctx-pack/v0`)

## Goal
Make cross-crate Rust semantic context **portable, cacheable, and reviewable** by defining:
- a reference CLI (`cargo semctx`),
- a normalized subject descriptor (`semctx-subject/v0`),
- a resolution/build-context record (`resolution-context/v0`),
- an input catalog for semantic sources (`semantic-input-catalog/v0`),
- a merge/completeness report (`semantic-merge-report/v0`),
- query/result artifacts (`semantic-query-report/v0`, optional `semctx-diff-report/v0`),
- and a bundle format (`semctx-pack/v0`).

Read this together with:
- [`design/semantic-context-lane-map.md`](./semantic-context-lane-map.md)
- [`design/semantic-context-pilot-program.md`](./semantic-context-pilot-program.md)
- [`proposals/epic-semantic-context-kit.md`](../proposals/epic-semantic-context-kit.md)

This is **not** “another indexer”, “yet another docs.rs mirror”, or “one universal Rust knowledge graph”.
The point is to give Rust tools one attachable boundary for answering questions like:
- which exact package/target/profile/feature/cfg/toolchain context is this query about?
- which semantic inputs were used (Cargo resolution facts, rustdoc JSON, rmeta, `rustc_public`, local builds, docs.rs cache)?
- what was merged exactly, and where is the result incomplete or approximate?
- which downstream answer is being claimed, and on what evidence?

## References (signals)
- Cargo plumbing goal: Cargo’s existing machine-facing surface is too thin, `cargo metadata` excludes feature resolution, and the build pipeline naturally breaks into phases like `resolve features` and `plan build`.
  https://rust-lang.github.io/rust-project-goals/2025h1/cargo-plumbing.html
- GSoC 2025 results: prototype plumbing commands implemented `resolve-features` and `plan-build`, showing clear demand for reusable Cargo phases.
  https://blog.rust-lang.org/2025/11/18/gsoc-2025-results/
- July 2025 goals update for `cargo-semver-checks`: docs.rs now hosts rustdoc JSON, but correct cross-crate work still needs recursive active dependency features and `rmeta`-based cross-crate combination.
  https://blog.rust-lang.org/2025/08/05/july-project-goals-update/
- docs.rs rustdoc JSON page: docs.rs builds and hosts rustdoc JSON; consumers must handle `format_version`; rustdoc JSON builds started on 2025-05-23.
  https://docs.rs/about/rustdoc-json
- StableMIR publication goal: publishing StableMIR crate(s) is meant to let tool developers analyze compiled crates and dependencies without compiler internals.
  https://rust-lang.github.io/rust-project-goals/2025h1/stable-mir.html
- GSoC 2025 results: `rustc_public` refactoring and versioning work was completed specifically to support the Rust tooling ecosystem.
  https://blog.rust-lang.org/2025/11/18/gsoc-2025-results/
- Cargo 1.93 development cycle: Cargo is explicitly thinking about unifying structured-report schemas with Cargo’s JSON output, partly to unlock a faster and more flexible `cargo fix` architecture.
  https://blog.rust-lang.org/inside-rust/2026/01/07/this-development-cycle-in-cargo-1.93/

## The missing seam
Rust now has several promising **semantic input lanes**, but they remain too loosely connected. The archive now needs an explicit lane map so local authoritative capture, public docs.rs cache, local-versus-remote comparison, fix/lint handoff, derived editor/assistant slices, and compiler-backed augmentation stop being narrated as one universal substrate.

Rust now has several promising **semantic input lanes**, but they remain too loosely connected:
- Cargo can resolve packages and plan builds,
- docs.rs can host rustdoc JSON,
- rustdoc JSON can expose documentation/type structure,
- `rmeta` and compiler internals know more than rustdoc JSON alone,
- `rustc_public` / StableMIR can support deeper compiler-aware tools,
- Cargo’s structured-report work and plumbing work are making machine-facing integration more plausible,
- and multiple downstream consumers (`cargo-semver-checks`, `cargo fix` successors, docs frontends, IDEs, review bots, assistants) need overlapping but not identical answers.

This gap matters more now than it would have a year ago. If docs remain canonical but more queries flow through IDEs, assistants, and tool-generated fix workflows, then Rust needs a **machine-usable context layer that stays attached to the canonical truth** instead of letting every consumer scrape, cache, and reinterpret the ecosystem differently.

The lane-correction note in [`design/semantic-context-lane-map.md`](./semantic-context-lane-map.md) should be treated as normative guidance for how this kit names authority, freshness, consumer power, and comparison posture.

What is still missing is one boring substrate that says:
1. what subject and build context are we talking about?
2. which semantic inputs were fetched or built?
3. what exact merge/composition happened across crates?
4. what remains unsupported, inferred, stale, or approximate?
5. which answer was derived from that context?

Without that, every tool keeps rebuilding its own partial workspace index, feature-resolution glue, cache story, and completeness heuristics.

## Core UX: `cargo semctx`
- `cargo semctx capture`
  - capture the selected subject and emit a `semctx-pack/v0`
- `cargo semctx explain <item|crate|feature|query-id>`
  - explain how a semantic answer was derived and from which lanes
- `cargo semctx query <kind>`
  - run a named semantic query over the captured context and emit `semantic-query-report/v0`
- `cargo semctx diff --against <pack|git-ref|path>`
  - compare semantic context or query answers and emit `semctx-diff-report/v0`
- `cargo semctx verify-pack <path>`
  - validate schema versions, digests, redaction, and attachment integrity
- `cargo semctx doctor`
  - identify missing lanes, stale cache entries, version mismatch, or unsupported feature combinations

The reference tool should start as an **adapter / packer / cache coordinator**.
It does not need to become a universal analysis engine.

See [`design/semantic-context-pilot-program.md`](./semantic-context-pilot-program.md) for the ranked rollout plan. The next credible move is not a universal workspace index or an assistant-facing blob; it is a staged pilot sequence proving local semver, docs.rs lookup, fix/lint handoff, and only then weaker editor/assistant slices and compiler-backed augmentation.

## Artifact family
### `semctx-subject/v0`
Describes the semantic subject under analysis:
- workspace/package/member identity
- root manifest and workspace slice
- target(s), profile(s), cfgs, feature set, resolver version
- host/target partition
- toolchain / `rustc` / Cargo identity
- source of truth class:
  - local workspace
  - CI build
  - docs.rs-derived subject
  - cached artifact subject
  - external attachment bundle

Design rule: **subject identity is first-class.**
A docs.rs-hosted JSON file, a local debug build, and a release CI pack are not interchangeable even if they describe “the same crate version”.

### `resolution-context/v0`
Records the exact dependency/build context used for semantic capture.

Should include:
- selected packages/versions/sources
- dependency-kind partitions (normal/build/dev/proc-macro)
- active features with provenance when available
- host vs target build units
- target-specific cfg activation
- build plan / unit identities when obtainable
- provenance class for each fact:
  - direct Cargo output
  - inferred from metadata/lockfile
  - imported from another report
  - manually supplemented

Design rule: **semantic context begins with exact build context, not with downstream queries.**

### `semantic-input-catalog/v0`
A catalog of semantic input lanes actually used.

Possible lanes:
- Cargo plumbing outputs (`resolve-features`, `plan-build`, etc.)
- `cargo metadata` / lockfile approximations
- local rustdoc JSON builds
- docs.rs rustdoc JSON fetches
- `rmeta` or compiler-side merge inputs
- `rustc_public` / StableMIR exports
- optional raw cargo report / diagnostics inputs

For each lane record:
- producer identity + version
- schema / format version
- cache location and digest
- freshness / staleness record
- target/profile/features/cfg assumptions
- whether the lane is authoritative, partial, fallback, or experimental

Design rule: **input provenance must survive caching.**
A cached docs.rs JSON fetch and a locally-built rustdoc JSON file may answer similar questions but they are not the same evidence.

### `semantic-merge-report/v0`
Explains how semantic inputs were combined.

Should capture:
- merge strategy used for this pack
- which crates or items were answered from which lane(s)
- whether combination relied on rustdoc JSON only, `rmeta` support, or deeper compiler/export lanes
- unresolved or lossy areas:
  - active dependency features not known precisely
  - foreign-item provenance ambiguous
  - missing rustdoc JSON or stale format version adapter
  - cross-crate merge blocked or partial
- comparability and confidence classification:
  - `authoritative`
  - `mixed-authoritative-and-inferred`
  - `best-effort`
  - `incomplete`

Design rule: **merge truth is not an implementation detail.**
The whole point is to stop tools from quietly turning partial inputs into overconfident semantic answers.

### `semantic-query-report/v0`
A normalized output for a named semantic query.

Example query families:
- `public-api-inputs`
- `foreign-item-provenance`
- `active-dependency-features`
- `doc-item-lookup`
- `type-bound-meaning`
- `candidate-fix-context`
- `editflow-handoff-context`
- `assistant-context-slice`

Each report should include:
- query id + version
- semantic subject and referenced input lanes
- answer payload
- explicit unsupported / ambiguous / approximate markers
- attached item/span/crate references where available
- stable reason codes instead of prose-only explanations

Design rule: **derived answers come after context capture.**
The pack should make it possible for many tools to ask different questions of one captured semantic subject.

## Edit/governance handoff
One near-term consumer should be [`design/edit-workflow-kit.md`](./edit-workflow-kit.md).

That handoff should look like:
- `cargo semctx` captures subject identity, resolution/build context, and semantic provenance;
- `cargo editflow` imports a pack reference or a bounded `semantic-query-report/v0`;
- candidate edits then point back to that context instead of rebuilding a hidden workspace index;
- and any assistant-facing slice remains a **derived view** over captured context, not a replacement for it.

Design rule: **semantic capture should be shareable across human review, Cargo/IDE tools, and assistant consumers without letting each consumer mint its own private canon.**


### `semctx-diff-report/v0`
A structured diff between two captured contexts or query results.

Should include:
- changed package/feature/cfg/toolchain context
- changed input-lane provenance
- changed merge confidence/completeness
- changed query answers with reason codes
- comparability classification:
  - comparable
  - partially comparable
  - incomparable

Design rule: **do not fake precision across mismatched semantic contexts.**

### `semctx-pack/v0`
Portable bundle containing:
- `semctx-subject.json`
- `resolution-context.json`
- `semantic-input-catalog.json`
- `semantic-merge-report.json`
- zero or more `semantic-query-report.json`
- optional `semctx-diff-report.json`
- checksums, redaction markers, provenance notes
- optional raw attachments:
  - rustdoc JSON blobs or fetch descriptors
  - Cargo plumbing outputs
  - docs.rs fetch receipts
  - `rustc_public` / StableMIR attachments
  - local build notes

## Design principles
1. **Lane identity is first-class.** Every capture, query, or diff should say whether it is local authoritative, public cache, comparison, fix/lint handoff, derived slice, or compiler-backed watch/augmentation.
- **Context first, consumer second.** The hard missing piece is the shared semantic subject, not one more consumer-specific report.
- **Keep lanes separate.** Cargo-plumbing facts, rustdoc JSON, `rmeta`-backed merges, and compiler exports should remain distinguishable.
- **Cache, but do not erase provenance.** Reuse must not make origin/freshness invisible.
- **Incompleteness is a feature.** “Could not determine recursively active features from available Cargo interfaces” should be a durable fact, not a silent fallback.
- **Composable queries beat bespoke indexes.** The same pack should support semver tooling, docs tooling, CI, and IDE/assistant consumers.
- **Redaction matters.** Private registry names, local paths, proprietary docs mirrors, and internal workspaces may need redaction without destroying structural value.

## What the kit should provide to others
- **Semver/public-API tools:** exact subject + semantic input provenance instead of hand-rolled rustdoc JSON + resolution glue.
- **Docs/search frontends:** cache-aware, version-aware inputs with explicit merge limits.
- **Cargo fix / lint / migration tools:** queryable semantic context that is closer to “what is actually built” than ad hoc loops.
- **IDE and editor tooling:** attachable workspace semantic packs for offline/debuggable analysis.
- **Assistant / review systems:** bounded context slices derived from one canonical capture rather than scraping docs and manifests independently.

## Overlap boundaries
- **Not Resolution Doctor Kit:** that kit explains version and feature selection; this kit consumes that context as one lane and adds semantic inputs above it.
- **Not Public API Kit:** that kit owns API diff / semver / MSRV verdicts; this kit owns the cross-crate semantic context those verdicts depend on.
- **Not MIR Analysis Kit:** MIR/`rustc_public` exports are one possible semantic lane here, but this kit is broader and shallower than MIR-specific analysis.
- **Not Compile Guidance Kit:** compile-time diagnostics and fix catalogs stay there; this kit only helps supply correct semantic context.
- **Not Ecosystem Atlas Kit:** Atlas curates stacks and guides; this kit captures semantic evidence about specific subjects/build contexts.
- **Not one universal workspace database:** packs can be partial, scoped, cached, and query-oriented.

## Hard problems (explicitly scoped)
1. **Recursive active-feature truth**
   - upstream work explicitly says this is not currently available through the lockfile or a Cargo interface; v0 must preserve that limitation honestly.
2. **Cross-crate merge fidelity**
   - rustdoc JSON alone is not always enough; `rmeta`/compiler-side combination may be necessary for correctness.
3. **Format/version churn**
   - docs.rs itself says consumers must check rustdoc JSON `format_version`; adapters must be explicit.
4. **Cache staleness and source mismatch**
   - local build outputs, docs.rs-hosted JSON, and CI-produced artifacts can drift.
5. **Toolchain-version comparability**
   - semantic answers across different toolchain versions may not be directly comparable.
6. **Scope explosion**
   - do not turn v0 into a universal query language for everything; start with a bounded query catalog and explicit raw attachments.

## Evaluation plan
Pilot on three classes of consumers:
1. a `cargo-semver-checks`-style cross-crate query needing correct dependency features and foreign-item provenance,
2. a docs/search/assistant frontend using docs.rs rustdoc JSON plus local resolution context,
3. a fix/lint/migration workflow wanting structured semantic context over actual build subjects.

Success bar:
- one pack can answer multiple materially different semantic queries,
- tools can distinguish authoritative versus best-effort answers,
- docs.rs/local/CI caches can be reused without hiding provenance,
- and downstream tools stop rebuilding incompatible workspace semantic indexes from scratch.
