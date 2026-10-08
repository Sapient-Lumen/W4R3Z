# Design: Compile Guidance Kit (`cargo guidance`, `guidance-pack/v0`)

## Goal
Define a portable contract for identifying, specifying, validating, diffing, and reviewing **developer-facing compile-time guidance and extension hooks** in the Rust ecosystem: diagnostics, lint catalogs, fix suggestions, compile-fail examples, and pipeline-hook metadata.

This should help answer questions like:
- what compile-time guidance a crate or tool intentionally provides,
- which lint ids and categories are part of its supported surface,
- which proc-macro, build, MIR-analysis, or delegated-build hooks it uses,
- what capabilities and determinism assumptions those hooks rely on,
- which examples define “good” diagnostics,
- and what evidence shows the guidance still works across toolchain or crate changes.

It should **not** replace rustc, Clippy, rust-analyzer, proc-macro APIs, or Cargo’s execution model.
It should make supportive compile-time UX reviewable.

## References (signals)
- Rust’s vision work explicitly recommends doubling down on extensibility, including better diagnostics and guidance from crates plus integration at more stages of the compilation workflow.
  https://blog.rust-lang.org/2025/12/19/what-do-people-love-about-rust/
- The diagnostic attribute namespace is now part of stable Rust, including `#[diagnostic::on_unimplemented]` and `#[diagnostic::do_not_recommend]`.
  https://doc.rust-lang.org/reference/attributes/diagnostics.html
  https://doc.rust-lang.org/beta/releases.html
- The 2026 flagships include establishing safety-critical lints in Clippy, which makes lint surfaces more central to Rust’s roadmap.
  https://rust-lang.github.io/rust-project-goals/2026/flagships.html
- StableMIR is being published to crates.io specifically so tool developers can build analysis tools without depending directly on compiler internals.
  https://rust-lang.github.io/rust-project-goals/2025h1/stable-mir.html
- Cargo-side experimentation on multiple build scripts / build-script delegation is evidence that build-time extension points are evolving toward more structure.
  https://blog.rust-lang.org/2025/11/18/gsoc-2025-results/
- `trybuild` is direct proof that compile-time diagnostics are already treated as a testable product surface in real Rust workflows.
  https://docs.rs/trybuild

## Design principles
1. **Guidance is part of the API.** If a crate teaches users through compile-time diagnostics, that surface deserves explicit artifact boundaries.
2. **Hooks must declare their posture.** Build-time and compile-time extension points need capability, determinism, and cacheability truth.
3. **Lints are not all the same thing.** Safety, style, policy, migration, and DSL guidance must not be flattened into one severity scalar.
4. **Examples beat screenshots.** Compile-fail and UI guidance examples should be first-class, versioned artifacts.
5. **Do not replace existing engines.** The kit should sit above rustc/Clippy/proc-macro/Cargo mechanisms and consume them through adapters.
6. **Keep compile-time and runtime guidance distinct.** This kit owns compiler/build/user-authoring surfaces, not application error contracts.

## Artifact family

### 1) `guidance-surface/v0`
Describes the supported compile/build-time user-facing surface of a crate or tool.

Fields should include:
- package / tool ids and versions
- supported guidance families (`diagnostic`, `lint`, `compile-fail-ui`, `macro-dsl`, `build-hook`, `analysis-hook`)
- stable ids or prefixes where applicable
- intended audiences (app devs, macro users, safety reviewers, embedded teams, etc.)
- toolchain/channel constraints
- explicit exclusions

### 2) `diagnostic-catalog/v0`
Defines compile-time diagnostics that are part of the intended surface.

Fields should include:
- diagnostic id
- title / summary
- emitting mechanism (trait diagnostic, proc-macro, lint, build hook, analyzer)
- primary span expectations
- notes / help / linked docs
- fix-it or machine-applicable status where relevant
- stability promise (stable id, best-effort wording, example-only, etc.)
- redaction / secrecy notes if diagnostics may expose configuration or paths

This artifact keeps compile-time guidance from being a pile of ad hoc strings.

### 3) `lint-catalog/v0`
Describes supported lint identities and governance-relevant metadata.

Fields should include:
- lint id / group
- source engine (`rustc`, Clippy, external lint pack, analyzer adapter)
- category (`safety`, `policy`, `style`, `migration`, `dsl`, `performance`, etc.)
- default level and recommended profiles
- standards / rule mappings where applicable
- machine-applicability / autofix posture
- false-positive notes / known limitations
- edition / toolchain dependencies

This is where the archive’s lint-governance ambitions become attachable and auditable.

### 4) `pipeline-hook-profile/v0`
Describes compile/build-time hooks used by the crate or tool.

Fields should include:
- hook id
- hook family (`proc-macro`, `build.rs`, delegated-build-step, StableMIR analysis, custom lint driver, codegen helper, generated-source step)
- inputs / outputs / trigger conditions
- required ambient capabilities or authority
- determinism / cacheability posture
- host/runtime assumptions
- feature-flag / target / platform restrictions
- security or review notes

This artifact is how extension power becomes visible instead of magical.

### 5) `guidance-example-catalog/v0`
Golden examples for guidance quality.

Fields should include:
- example id
- scenario description
- source snippet or fixture pointer
- expected diagnostic/lint ids
- expected help/fix posture
- normalization rules (paths, versions, spans)
- toolchain assumptions

This elevates `trybuild`-style and UI-test expectations into a portable surface.

### 6) `guidance-check-report/v0`
Records what was actually checked.

Fields should include:
- surface / catalog versions
- diagnostics/lints/examples exercised
- pass/fail/partial/skipped status
- toolchain and environment details
- normalization / diff notes
- attached raw outputs or snapshots
- hook-capability observations

### 7) `guidance-pack/v0`
Bundle of the above plus human-facing docs, rationale, and migration notes.

## CLI shape
`cargo guidance` should start as a thin adapter/orchestrator.

Potential commands:
- `cargo guidance init` — scaffold a guidance surface
- `cargo guidance export` — emit catalogs from current metadata/tests/config
- `cargo guidance check` — run examples and validate declared guidance/hook posture
- `cargo guidance diff` — compare guidance surfaces across versions
- `cargo guidance pack` — assemble `guidance-pack/v0`

The CLI should prefer pointers and normalized snapshots over giant embedded blobs.

## Initial targets
The first credible version should **not** try to model every future compiler extension.
It should start where there is already concrete ecosystem evidence and move through a ranked pilot program rather than a universal extension manifest.
1. **trait diagnostics and crate-authored compiler guidance**
   - `#[diagnostic::on_unimplemented]`
   - `#[diagnostic::do_not_recommend]`
2. **proc-macro UI guidance**
   - proc-macro crates with `trybuild`-style compile-fail examples
3. **lint catalogs and safety-oriented lanes**
   - Clippy-backed or analyzer-backed lint groups with explicit ids and severity posture
4. **build / analysis hook metadata**
   - `build.rs`, delegated-build experiments, and StableMIR-backed analyzers recorded honestly as hook profiles

This matters: the kit should support both **today’s stable guidance surfaces** and **tomorrow’s richer compiler-extensibility lanes** without pretending they are identical.

## What good adoption looks like
A good v1 does not need every macro crate in the ecosystem.
It needs a few credible proofs that the artifacts clarify real work.

Success would look like:
- one trait-diagnostic pilot with explicit stability posture,
- one macro-heavy crate shipping a stable guidance surface and example catalog,
- one lint-oriented stack publishing a lint catalog with explicit standards/profile posture,
- one build/analyzer tool publishing honest hook metadata,
- one CI/editor integration consuming a guidance pack,
- and one migration diff showing guidance drift between releases.

## Boundaries with other archive proposals
- **Diagnostic Surface Kit** owns runtime/application failure contracts, not compiler/build guidance.
- **Lint Baseline Kit** owns rollout, debt baselines, and governance over lint findings once lint identities exist.
- **Build Extension Kit** owns declarative build-step uplift and artifact movement, not developer-facing diagnostic surfaces.
- **Compile-Time Capabilities Kit** owns sandboxing and authority for build.rs / proc-macros; this kit consumes that truth instead of replacing it.
- **MIR Analysis Kit** owns stable compiler-analysis export surfaces; this kit can describe the user-facing guidance/hook layer of tools built on top.
- **Macro Workflow Kit** inventories and reviews macro-heavy workflows; this kit makes the user-facing guidance those workflows emit more portable.

## Failure modes to avoid
- a universal “extension manifest” that pretends every future compiler hook is already understood;
- catalogs with ids but no runnable examples;
- treating warning text snapshots as the whole contract while ignoring spans, help, and fix posture;
- flattening runtime/app diagnostics into compile-time guidance;
- or using the kit to bypass proper review of unsafe or authority-heavy hooks.

See [`design/compile-guidance-pilot-program.md`](./compile-guidance-pilot-program.md) for the ranked rollout plan. The next credible move is not another proc-macro helper, lint bundle, or stderr snapshot archive; it is a staged pilot sequence proving trait-diagnostic, proc-macro UI, lint-catalog, hook-profile, and CI/editor consumption lanes.
See also [`design/canonical-learning-consumer-pilot-program.md`](./canonical-learning-consumer-pilot-program.md): the next shared stack move above Compile Guidance is an explicit downstream import contract so CI, editors, assistants, and review tooling can consume guidance artifacts without silently becoming the canonical guidance surface themselves.
