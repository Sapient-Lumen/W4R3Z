---
id: P-0536
title: Crate Knowledge Pack Kit — canonical API/docs/example bundles for search, support, and assistant-grade crate understanding
status: idea
domains: [docs, rustdoc, docsrs, examples, search, support, assistants, tooling]
last_reviewed: 2026-03-23
evidence:
  - https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
  - https://docs.rs/about/rustdoc-json
  - https://doc.rust-lang.org/cargo/reference/unstable.html#output-format-for-rustdoc
  - https://rust-lang.github.io/rfcs/2963-rustdoc-json.html
  - https://docs.rs/about/builds
  - https://docs.rs/about/metadata
  - https://docs.rs/about/download
  - https://docs.rs/about/redirections
  - https://docs.rs/about/builds
  - https://doc.rust-lang.org/cargo/commands/cargo-metadata.html
  - https://rust-lang.github.io/rfcs/3662-mergeable-rustdoc-cross-crate-info.html
---

# Problem

Rust now has enough documentation substrate to power much better machine-readable crate guidance, but it is still scattered across too many lanes for ordinary maintainers and downstream users to rely on cleanly.

The current state is surprisingly strong in pieces:

- docs.rs hosts HTML docs *and* rustdoc JSON for published crates;
- Cargo and rustdoc can emit JSON output for tools;
- docs.rs documents real hosted-build behavior, metadata knobs, cross-compilation posture, and sandbox limits;
- the archive already has strong ideas for rustdoc JSON normalization, docs.rs parity evidence, doctest extraction, and docs coverage review.

But the people who actually need help still usually cannot ask one boring question and get one boring answer:

- “What is the canonical public API and where are the most trustworthy docs for it?”
- “Which examples are official, runnable, feature-gated, target-gated, or merely illustrative?”
- “Which facts are straight from rustdoc/docs.rs and which were inferred?”
- “Which docs were actually visible on docs.rs?”
- “What small slice should I hand a support engineer, search indexer, or coding assistant without making them scrape everything themselves?”
- “Which classes of questions is that compact slice actually allowed to answer, and which should it refuse or route to manual review?”
- “Which exported summary claims can be traced back to exact excerpts and source-material IDs?”

The 2025 State of Rust survey makes the missing layer sharper.
It says online documentation remains the preferred canonical reference, that studying the code itself remains a major learning route, and that some learning activity appears to be moving toward LLM tooling.
That combination raises the bar: Rust crates increasingly need a way to package **canonical documentation truth** for both humans and machine consumers.

The missing crate is therefore **not** another docs portal, **not** another rustdoc JSON parser, **not** another docs coverage percentage tool, and **not** a “chat with your crate” gimmick.

The missing crate is a **Crate Knowledge Pack Kit**:
a receiver-facing contract that joins API surface, rendered-doc provenance, examples, doctest/support posture, feature/target visibility, and compact query slices into one reusable bundle.

# Main judgment

A worthy crate in this lane should let another person answer all of these cleanly:

1. **What public items exist, and which path/source/rendered-doc pages define them?**
2. **Which examples are official, where did they come from, and how runnable are they?**
3. **Which docs facts come from rustdoc/docs.rs directly, and which are conservative inference?**
4. **Which feature flags / targets / cfgs materially change what users can see or run?**
5. **What small package should be handed to search tools, support tools, or assistants without scraping the whole crate?**
6. **Which question classes can that compact package answer honestly, and which claims remain manual-review-only?**

If a candidate crate cannot answer those questions, it is still mostly substrate or wrapper.

# What it provides

- `crate-knowledge.toml` — maintainer policy for what to include, redact, slice, and publish.
- `api-surface.receipt.json` — normalized public-item inventory with path, visibility, source provenance, and rustdoc identity.
- `docs-source.manifest.json` — mapping from API items to rustdoc HTML, rustdoc JSON, README/book/example sources, and docs.rs pages when available.
- `example-lineage.report.json` — official examples, README snippets, doctests, generated examples, feature/target gates, and execution/support class.
- `feature-target-visibility.report.json` — which item/example/doc surfaces are hidden, gated, or lane-specific.
- `docsrs-presence.import.json` — what docs.rs rendered, on which default/selected targets, and where hosted posture diverged from local intent.
- `material-basis.receipt.json` — exact hosted/local/versioned/floating materials imported into the pack, including rustdoc JSON format/version caveats and docs.rs download/archive notes.
- `knowledge-slice.manifest.json` — small themed slices such as `getting_started`, `public_api_minimal`, `runtime_support`, `ffi_surface`, or `async_usage`.
- `export-policy.receipt.json` — consumer-profile, redaction, pinning, and hosted-vs-local precedence rules for a compact public or machine-consumable export.
- `excerpt-lineage.report.json` — exact exported fragments and the source-material IDs they came from.
- `assistant-context.pack.json` — compact machine-consumable export with stable sections, supported query classes, refusal/manual-review zones, provenance, and links back to the other review artifacts.
- `query-support.matrix.json` — which question classes are `supported`, `partial`, `manual_review_required`, or `refused`, together with the artifacts and evidence basis that justify that status.
- `claim-trace.report.json` — maps exported summary claims back to exact excerpt IDs and source-material IDs, with exactness and manual-review flags.
- `citation-locator.receipt.json` — resolves exported excerpts and claims to pinned, target-aware citation locators, keeping floating docs.rs shorthand and fallback routes explicit.
- `citation-capability.report.json` — states which query classes can honestly cite item/page/package-level locators and which still require manual review.
- `item-witness.manifest.json` — binds exported excerpts and claims to reviewable crate/version/target/path/kind/source-span witnesses while keeping raw rustdoc JSON IDs visibly blob-local.
- `identity-fidelity.report.json` — classifies when a witness is exact, target-bound, cross-version-rechecked, approximate, or manual-review-only.
- `knowledge-diff.report.json` — compare two crate-knowledge bundles and classify API-doc, example, visibility, provenance, or citation-route drift.
- `knowledge-pack.manifest.json` — top-level manifest tying the receipts and reports together.
- `cargo crate-knowledge pack` — emit a complete bundle for a workspace or crate.
- `cargo crate-knowledge slice <profile>` — emit a focused pack for support or machine consumers.
- `cargo crate-knowledge diff <old> <new>` — compare two bundles across releases or branches.
- `cargo crate-knowledge doctor` — flag suspicious cases such as undocumented public APIs, examples with unclear lineage, docs.rs-hosted divergence, feature-gated items with no visible support notes, or “supported” query classes without citation-ready locator coverage.
- `cargo crate-knowledge resolve-locators <bundle>` — emit citation-locator receipts for exported sections and claims without turning the crate into an answer bot.
- `*.crateknowledge.zip` — portable artifact for search, support, docs review, and assistant indexing.

# What the crate should provide other people

1. **One canonical crate handoff pack** instead of bespoke scraping of HTML docs, READMEs, examples, and rustdoc JSON.
2. **One provenance-aware API/docs map** that keeps direct rustdoc facts separate from inference.
3. **One example-lineage answer** that distinguishes official runnable examples from illustrative snippets and generated output.
4. **One visibility map** for feature/target/cfg-sensitive surfaces.
5. **One exact material-basis answer** for what hosted/local/versioned/floating materials were actually imported.
6. **One machine-readable slice format** for support systems, local search, and assistant tooling.
7. **One export-policy receipt** so maintainers can safely publish useful knowledge without dumping private scaffolding or silently relying on floating materials.
8. **One excerpt-lineage answer** for which concrete fragments entered a compact slice.
9. **One query-support matrix** so support/search/assistant consumers know what the bundle can answer without improvisation.
10. **One claim-trace report** so compact summaries can be audited back to exact excerpts and materials.
11. **One diff artifact** for release review so docs/example/API-support drift becomes visible.
12. **One citation-locator receipt** so downstream tools know which pinned, target-aware URLs or archive paths are actually safe to cite.
13. **One citation-capability report** so supported query classes do not silently over-claim citation fidelity.
14. **One item-witness manifest** so another tool can tell which conceptual item a claim was tied to without mistaking raw rustdoc JSON IDs for durable public identifiers.
15. **One identity-fidelity report** so reused witnesses across versions or targets are explicitly marked exact, rechecked, approximate, or manual-review-only.

# Persona / who it’s for

- library and framework maintainers
- docs/tooling authors
- search/indexing authors
- support engineers handling “how do I use this crate?” questions
- teams building local assistants, code search, or upgrade review workflows over Rust crates

# Users & user stories

- **Maintainer**: “Give me one canonical pack of our public API, official examples, and docs support notes that downstream tools can consume.”
- **Support engineer**: “I need a compact, provenance-aware view of the crate’s intended entry points and examples.”
- **Docs reviewer**: “Show me which public APIs have docs, examples, and docs.rs-hosted presence, and what changed this release.”
- **Search / assistant author**: “I want a stable crate-shaped export instead of scraping rustdoc HTML and guessing what is canonical.”

# Prior art (and why it’s insufficient)

- **P-0051 `rustdoc-json-kit`** is about generation, caching, and multi-version normalization of rustdoc JSON. That is essential substrate, but it does not by itself say which docs/examples/README slices are the maintainer-approved handoff surface.
- **P-0472 Docs.rs Build Parity & Evidence Kit** is about hosted-vs-local documentation build truth. That explains parity, but it is not the end-user knowledge pack.
- **P-0476 Rustdoc Coverage Review Bundle Kit** is about docs coverage snapshots and API-surface debt. That gives review signals, but not a canonical reusable export.
- **P-0455 Doctest Extraction & Support Contract Kit** is about doctest extraction and execution truth. That is one important evidence source, not the whole crate knowledge surface.
- Rustdoc JSON and docs.rs already exist as raw substrate, but they are still too low-level and too fragmented for ordinary support/search/assistant consumers.

What remains missing is the **joined, provenance-aware handoff artifact**.

# Design goals

1. **Canonicality first** — prefer maintainer-declared official entry points over blind scraping.
2. **Provenance explicit** — keep rustdoc/docs.rs facts, imported facts, and inference separate.
3. **Sliceability** — support small exports for focused use cases.
4. **Pinability** — packs must say when materials are exact vs floating.
5. **Diffability** — release-to-release change review must be straightforward.
6. **Redaction-aware** — allow excluding private/internal-only or unreviewed materials.
7. **Tool-neutral** — useful for local search, support workflows, CI review, and assistant pipelines without hardcoding one vendor.

# Non-goals

- Hosting or rendering a full alternative docs portal.
- Replacing rustdoc, docs.rs, or cargo-docs-rs.
- Guaranteeing that every machine consumer interprets the bundle perfectly.
- Turning untrusted generated prose into canonical guidance without maintainer approval.
- Owning prompt engineering, retrieval ranking, or answer-generation policy for downstream assistant products.

# Architecture & API sketch

- Core library types:
  - `CrateKnowledgeProfile`
  - `ApiSurfaceReceipt`
  - `DocsSourceManifest`
  - `ExampleLineageReport`
  - `FeatureTargetVisibilityReport`
  - `DocsRsPresenceImport`
  - `MaterialBasisReceipt`
  - `KnowledgeSliceManifest`
  - `ExportPolicyReceipt`
  - `ExcerptLineageReport`
  - `AssistantContextPack`
  - `QuerySupportMatrix`
  - `ClaimTraceReport`
  - `KnowledgeDiffReport`
  - `KnowledgePackManifest`
- Core library functions:
  - `capture_crate_knowledge_pack()`
  - `import_rustdoc_json()`
  - `import_docsrs_presence()`
  - `capture_material_basis()`
  - `build_example_lineage()`
  - `compute_visibility_report()`
  - `apply_export_policy()`
  - `slice_pack()`
  - `emit_excerpt_lineage()`
  - `diff_packs()`
  - `write_pack()`
- Cargo-facing workflows:
  - `cargo crate-knowledge pack`
  - `cargo crate-knowledge slice`
  - `cargo crate-knowledge diff`
  - `cargo crate-knowledge doctor`
- Storage model:
  - content-addressed sub-artifacts for rustdoc/API/example imports
  - explicit manifest edges so consumers can ignore sections they do not trust or need

# Security / safety model

- Treat imported docs/JSON/README/example content as untrusted input.
- Preserve provenance and exactness classes so generated or inferred content does not masquerade as canonical maintainer guidance.
- Make redaction first-class for internal paths, test-only artifacts, or support-only notes.
- Avoid executing arbitrary examples by default; execution receipts should be imported from dedicated doctest/example support lanes.

# Maintenance & governance plan

- Keep the bundle schema conservative and versioned.
- Reuse existing substrate crates and upstream formats instead of cloning them.
- Maintain a clear boundary against P-0051, P-0472, P-0476, and P-0455 so this lane does not sprawl.
- Prefer importing upstream facts over inventing parallel truth.

# Milestones

- **0.1**: API-surface receipt + docs-source manifest + example-lineage report + minimal pack writer.
- **0.2**: docs.rs presence import + feature/target visibility report + material-basis receipt + slice profiles.
- **0.3**: export-policy receipt + excerpt-lineage report + assistant-context pack export.
- **0.4**: query-support matrix + claim-trace report + doctor checks for unsupported/overclaimed question classes.
- **0.5**: maintainer-declared canonical entrypoint profiles and stronger redaction/pinning/refusal policies.

# Open questions

- How much of the pack should be derivable automatically versus maintainer-declared?
- Which slice profiles are generic enough to standardize early?
- How should README/book/tutorial content be linked without overfitting to one docs stack?
- Which exact rustdoc JSON compatibility story should be imported from P-0051 versus re-expressed locally?

# Sources

See front matter links.


## 2026-03-23 citation-locator addendum

The next missing layer in this lane is not a better chatbot.
It is a better answer for **what should be cited**.

Fresh docs.rs and Cargo sources now make three truths too concrete to ignore:

1. docs.rs shorthand URLs are intentionally convenient and often floating;
2. hosted docs surfaces are target-aware rather than one universal page set;
3. compact packs can support some question classes honestly while still lacking citation-ready support for others.

That means **P-0536** should now standardize:

- `citation-locator.receipt.json`
- `citation-capability.report.json`
- and doctor checks that reject fake citation certainty.

Sources:
- https://docs.rs/about/redirections
- https://docs.rs/about/builds
- https://docs.rs/about/rustdoc-json
- https://docs.rs/about/download
- https://doc.rust-lang.org/cargo/commands/cargo-rustdoc.html
- https://doc.rust-lang.org/cargo/commands/cargo-metadata.html

# 2026-03-23 build-surface / conditioned-availability addendum

The next high-leverage move is **not** a retrieval UI.
It is to make visible crate knowledge recipe-aware.

Promote these two artifacts to first-class status:

- `build-surface.receipt.json`
- `conditioned-availability.report.json`

Working rule:
- do not claim an item/example/docs surface is simply “available” unless the pack can say what feature/target/docs-build recipe produced that visibility,
- do not reuse an item witness as if it were also an availability witness,
- and do not treat docs.rs hosted pages as one universal page set when metadata/targets/toolchain recipe materially shaped them.
