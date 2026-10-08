# Design: Semantic Context Authority Lane Map (local authoritative capture, docs.rs cache lanes, derived slices, and compiler-backed augmentation)

## Goal
Make the archive more precise about **what kind of semantic-context claim is actually being made**.

Rust’s machine-readable story is getting stronger, but the ecosystem still talks too often as if one phrase — “semantic context” — names one unified thing.
It does not.
A local workspace capture built from explicit Cargo phases and local artifacts, a public docs.rs rustdoc-JSON lookup, a local-versus-remote comparison, a fix/lint handoff, an editor or assistant slice, and an experimental compiler-backed merge are **different but linked** lanes.

The worthy contribution here is therefore not one more hidden workspace index and not a generic “AI context for Rust” blob.
It is a **portable lane map and evidence boundary** that lets tools say which semantic lane they are using, what authority it actually has, what freshness/completeness limits apply, and which downstream consumers may reuse it honestly.

Read this together with:
- [`design/semantic-context-kit.md`](./semantic-context-kit.md)
- [`design/semantic-context-pilot-program.md`](./semantic-context-pilot-program.md)
- [`design/edit-workflow-kit.md`](./edit-workflow-kit.md)
- [`design/compile-guidance-kit.md`](./compile-guidance-kit.md)
- [`proposals/epic-semantic-context-kit.md`](../proposals/epic-semantic-context-kit.md)

## Why this note is needed now
The current official and ecosystem signals line up around one conclusion: Rust needs a better **semantic-context contract**, not just more semantic consumers.

- The accepted 2025H1 Cargo plumbing goal says Cargo’s current machine-facing surface is too thin, that `cargo metadata` can include dependency resolution but excludes feature resolution, and that builds naturally decompose into phases such as **resolve features** and **plan build**.
  https://rust-lang.github.io/rust-project-goals/2025h1/cargo-plumbing.html
- The 2025 GSoC results say prototype plumbing commands like `resolve-features` and `plan-build` were actually implemented, which is strong evidence that reusable semantic-subject capture is no longer just a design sketch.
  https://blog.rust-lang.org/2025/11/18/gsoc-2025-results/
- The July 2025 project-goals update for `cargo-semver-checks` says docs.rs-hosted rustdoc JSON is helpful as a cache, but correct cross-crate work still needs recursively active dependency features and `rmeta`-based combination. That is exactly the kind of split a lane map should preserve instead of hiding.
  https://blog.rust-lang.org/2025/08/05/july-project-goals-update/
- docs.rs now hosts rustdoc JSON directly and explicitly tells consumers to check `format_version`, which means public cached semantic data is real infrastructure but not a drop-in substitute for every local build subject.
  https://docs.rs/about/rustdoc-json
- The StableMIR publication goal exists so tool developers can analyze compiled crates and dependencies without relying on compiler internals, and the 2025 GSoC results say `rustc_public` refactoring/versioning work landed for the tooling ecosystem. That gives Rust a plausible deeper lane, but not one that should be narrated as universally ready today.
  https://rust-lang.github.io/rust-project-goals/2025h1/stable-mir.html
  https://blog.rust-lang.org/2025/11/18/gsoc-2025-results/
- Cargo’s 1.93 development-cycle post says schema work could improve Cargo JSON output and help unlock a faster, more flexible `cargo fix` architecture. That means fix/lint/edit consumers increasingly need a reusable context layer rather than bespoke private indexes.
  https://blog.rust-lang.org/inside-rust/2026/01/07/this-development-cycle-in-cargo-1.93/
- The 2025 State of Rust survey says online documentation remains the preferred canonical reference even while LLM/editor workflows are rising. That is a direct warning against letting derived machine slices masquerade as canonical Rust truth.
  https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/

That is enough evidence to stop asking “what is Rust’s semantic context story?” and start asking **which semantic lane is under review, which facts are authoritative, which are cached or derived, and which remain watch-only?**

## The lane map

### Lane 1 — Local authoritative workspace capture
**What it is**
- A semantic subject captured from a local workspace/package/target/profile/feature/toolchain context.
- Prefer explicit Cargo phase outputs, local rustdoc JSON, and other local subject-bound artifacts over folklore or reverse-engineered cache state.

**Why it matters**
- This is the highest-authority practical lane for many real consumers.
- It is the cleanest way to answer semver/public-API, migration, CI, and review questions about one exact subject.

**What the archive should preserve**
- exact `semctx-subject/v0` identity,
- Cargo/plumbing and resolution/build-context provenance,
- local artifact provenance,
- feature/cfg/toolchain posture,
- and explicit incompleteness markers when some local semantic source was unavailable.

**What it should not pretend**
- that `cargo metadata` alone proves complete semantic truth,
- that one local build subject automatically generalizes to public release or docs.rs subjects,
- or that higher-authority local capture can be reconstructed later from a derived editor payload.

### Lane 2 — Public release / docs.rs cache lane
**What it is**
- Semantic questions answered from public rustdoc-JSON or related release-facing cache material, especially docs.rs-hosted artifacts.

**Why it matters**
- Rust’s canonical docs surface is public and widely reused.
- This lane enables machine-usable lookup and navigation for released crates without forcing every consumer to rebuild everything locally.

**What the archive should preserve**
- docs.rs or public-cache provenance,
- release/package identity distinct from local workspace identity,
- `format_version` posture,
- freshness/age of the cached artifact,
- and explicit unsupported areas versus local authoritative capture.

**What it should not pretend**
- that public docs.rs cache equals the exact local workspace state under review,
- that a successful docs.rs fetch proves recursive feature truth,
- or that public rustdoc JSON alone answers deeper compiler-backed questions.

### Lane 3 — Local-versus-remote comparison lane
**What it is**
- A deliberate comparison between two semantic lanes, most often local authoritative capture versus public docs.rs/release cache.

**Why it matters**
- Teams increasingly need to know not only “what does this lane say?” but “how does local reality differ from the public/released semantic surface?”
- This is crucial for PR review, release validation, drift detection, semver debugging, and support handoff.

**What the archive should preserve**
- explicit two-subject comparability,
- which differences are authoritative versus advisory,
- freshness mismatch and stale-cache posture,
- unsupported comparison classes,
- and whether the result is fully comparable, partially comparable, or incomparable.

**What it should not pretend**
- that every local-vs-remote question has a crisp yes/no answer,
- that stale docs.rs cache is merely an implementation detail,
- or that comparison output is the same thing as canonical capture.

### Lane 4 — Fix/lint/edit semantic handoff lane
**What it is**
- A bounded semantic-context export whose job is to support fix/lint/migration/edit consumers without forcing them to build their own hidden workspace index.

**Why it matters**
- Cargo and lint/edit work are moving toward more structured, selective, schema-aware flows.
- This lane is the honest bridge from semantic capture into edit execution and review.

**What the archive should preserve**
- which semantic query families are being handed off,
- which consumer class is allowed to rely on them,
- which parts are authoritative versus fallback,
- and what the edit-side consumer must still verify independently.

**What it should not pretend**
- that semantic handoff is the same thing as edit selection or apply truth,
- that every fix/lint workflow needs the full semantic graph,
- or that a fast edit workflow can erase subject/provenance limits.

### Lane 5 — Derived editor / assistant slice lane
**What it is**
- A weaker, bounded rendering of semantic context for editors, assistants, navigation helpers, and question-answering tools.

**Why it matters**
- This is increasingly how many users encounter Rust information in practice.
- The survey signal makes it important, but also makes the boundary more important: derived slices must stay anchored to canonical artifacts.

**What the archive should preserve**
- which canonical artifacts were imported,
- what was omitted or compressed,
- freshness and redaction posture,
- explicit consumer limits,
- and a clear distinction between captured truth and rendered/derived view.

**What it should not pretend**
- that a chat/editor slice is canonical semantic evidence,
- that omitted provenance can be reconstructed from the slice later,
- or that assistant convenience justifies flattening authoritative and fallback lanes into one answer.

### Lane 6 — Compiler-backed augmentation watch lane
**What it is**
- Experimental or partially-ready augmentation using `rmeta`, StableMIR, `rustc_public`, or related compiler-backed interfaces.

**Why it matters**
- This is the most powerful prospective lane.
- It may eventually let tools answer questions that rustdoc JSON and Cargo plumbing cannot answer well.
- But it is also the easiest lane to overclaim.

**What the archive should preserve**
- explicit experimental/watch posture,
- what compiler-backed input was actually used,
- what remained local/public authoritative versus augmented,
- and where the lane is incomplete, unstable, or consumer-limited.

**What it should not pretend**
- that compiler-backed augmentation is already the one stable answer for all tooling,
- that experimental analysis should silently overwrite local/public capture truth,
- or that “deeper” automatically means “more reusable”.

## Shared artifact spine
A credible ecosystem contribution should let these lanes share a thin artifact spine without flattening them.

Prefer a family like:
- `semctx-subject/v0` — the reviewed semantic subject
- `resolution-context/v0` — Cargo/resolution/build-context facts for that subject
- `semantic-input-catalog/v0` — local/public/compiler-backed input inventory with lane identity
- `semantic-merge-report/v0` — completeness, merge class, and unsupported-area truth
- `semantic-query-report/v0` — bounded answers for named consumers
- `semctx-diff-report/v0` — local-vs-remote or revision-to-revision semantic comparison
- `semctx-consumer-handoff/v0` — which downstream consumer class is allowed to claim what
- `semctx-lane-profile/v0` — authoritative/fallback/freshness rules for the lane
- `semctx-readiness-report/v0` — `promote` / `pilot` / `watch` / `defer` verdicts for the lane
- `semctx-pack/v0` — attachable bundle joining the above without pretending every consumer needs every artifact

That spine should make it possible to say:
- **which semantic lane is in play,**
- **what authority/freshness it has,**
- **which consumer may reuse it,**
- and **what was still missing or lossy.**

## What Semantic Context Kit should import from this note
The next credible move is **not** a separate “Rust knowledge graph stack”.
It is to let **Semantic Context Kit** publish lane truth explicitly inside:
- `semctx-subject/v0`
- `semantic-input-catalog/v0`
- `semantic-merge-report/v0`
- `semantic-query-report/v0`
- selected `semctx-diff-report/v0`
- and `semctx-pilot-pack/v0`

At minimum, semantic-context exports should preserve:
- `semantic_lane`: `local_authoritative` / `public_cache` / `comparison` / `fix_lint_handoff` / `derived_slice` / `compiler_backed_watch`
- subject class (`workspace`, `package`, `release`, `docsrs_release`, `comparison_pair`, `derived_export`)
- authority posture (`authoritative`, `release_cache`, `derived`, `experimental`, `mixed`)
- freshness posture (`captured_now`, `release_cached`, `stale_possible`, `explicitly_stale`, `mixed`)
- completeness posture (`complete_for_lane`, `partial`, `best_effort`, `unknown`)
- consumer class (`semver`, `docs_lookup`, `review_ci`, `fix_lint`, `editor`, `assistant`, `analysis_tool`)
- canonical-import refs and omitted/derived-area refs when relevant
- comparison class (`not_applicable`, `fully_comparable`, `partially_comparable`, `incomparable`) when the lane is a comparison lane

And `semctx-diff-report/v0` should preserve semantic drift such as:
- local subject ↔ public release/docs.rs drift,
- old cache ↔ fresh cache drift,
- rustdoc-only ↔ compiler-augmented drift,
- canonical capture ↔ derived slice reduction,
- and changed consumer/query-budget posture.

## What a worthy contribution should look like in theory and practice
A worthy Rust contribution here would be a **thin semantic-context lane profiler and verifier** above Cargo, rustdoc, docs.rs, and compiler-backed inputs rather than another workspace index or assistant wrapper.

In practice that means:
1. one reviewable export that says **which semantic lane** a pack or query is actually using;
2. explicit statements about subject identity, authority, freshness, and unsupported areas;
3. comparison reports that keep local-versus-public drift visible instead of implicit;
4. consumer-handoff artifacts that say what fix/lint/editor/assistant consumers may legitimately claim;
5. a watch lane for compiler-backed augmentation that can mature without overwriting simpler lanes prematurely.

That contribution would help:
- semver/public-API tooling that needs exact local subject truth,
- docs/search/navigation tooling that wants public-cache reuse without local-build confusion,
- fix/lint/edit systems that need bounded semantic handoff,
- editor and assistant tools that should stay attached to canonical evidence,
- and future compiler-backed tooling that should graduate through explicit watch/pilot lanes instead of hype.

## Non-goals
- replacing Cargo, rustdoc, docs.rs, StableMIR, or `rustc_public`;
- inventing one universal Rust semantic graph for every consumer;
- pretending local authoritative capture, public cache, derived slices, and compiler-backed augmentation are interchangeable;
- merging edit execution truth into semantic capture truth;
- or letting assistant/rendered views silently become the canon.
