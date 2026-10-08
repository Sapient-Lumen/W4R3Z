# Design: Retrieval Surface Kit (`cargo retrievecheck`, `retrieval-pack/v0`)

## Goal
Define a portable contract for declaring, validating, diffing, and reviewing a Rust program’s supported retrieval/search surface: corpora, indexes, query modes, filters/facets/highlights, ranking and hybrid-retrieval posture, checked query cases, and evidence that the declared retrieval surface still matches the program.

This should **not** replace Tantivy, Quickwit, LanceDB, Qdrant, Meilisearch, `usearch`, or future Rust-native retrieval systems.
It should make them compose better and make support claims reviewable.

## References (signals)
- `tantivy` is explicitly “a search engine library. Think Lucene, but in Rust.”
  https://docs.rs/tantivy/latest/tantivy/
- Tantivy already exposes snippet generation and hierarchical facets, which are user-visible search-surface semantics.
  https://docs.rs/tantivy/latest/tantivy/snippet/index.html
  https://docs.rs/tantivy/latest/tantivy/schema/struct.Facet.html
- Quickwit’s index config already separates index storage location, doc mapping, indexing settings, and search settings like `default_search_fields`.
  https://quickwit.io/docs/configuration/index-config
- Quickwit explicitly distinguishes fixed-schema, schemaless, and mixed indexing modes.
  https://quickwit.io/docs/overview/concepts/indexing
- LanceDB explicitly positions itself for vector, full-text, and hybrid retrieval applications.
  https://docs.lancedb.com/
- LanceDB hybrid search explicitly combines vector and full-text search and supports reranking, including custom rerankers.
  https://docs.lancedb.com/search/hybrid-search
  https://docs.rs/lancedb/latest/lancedb/rerankers/trait.Reranker.html
- Qdrant’s Rust client already exposes search/query operations for collections, while Qdrant’s hybrid-query docs explicitly support staged/prefetch + rescore retrieval.
  https://docs.rs/qdrant-client/latest/qdrant_client/
  https://qdrant.tech/documentation/concepts/hybrid-queries/
- Meilisearch now treats full-text, semantic, and hybrid search plus embedder setup as normal product features.
  https://www.meilisearch.com/solutions/hybrid-search
  https://www.meilisearch.com/docs/learn/ai_powered_search/getting_started_with_ai_search
- `usearch` shows Rust also has a lower-level ANN/index lane with explicit dimensions, metrics, search parameters, persistence, and memory posture.
  https://docs.rs/usearch/latest/usearch/struct.Index.html

## Core components

### 1) `retrieval-surface/v0`
A design-time declaration of the supported retrieval boundary for a binary/service/workspace.

Required ideas:
- system/service identity
- corpora/indexes in scope
- query families in scope:
  - full-text
  - exact structured filtering
  - ANN/vector
  - hybrid full-text + vector
  - multistage retrieval
  - reranked retrieval
  - browse/facet-oriented discovery
- support classes:
  - official
  - best-effort
  - experimental
  - deprecated
  - internal
- linked attachments:
  - service/event surfaces
  - model/tokenizer profiles
  - dataset/schema attachments
  - settings/support-envelope assumptions
  - observability and diagnostic ids

Design rule: preserve keyword/full-text, vector/ANN, hybrid, and reranked retrieval as related but distinct lanes. Do not flatten them into one fake generic “search mode.”

### 2) `corpus-profile/v0`
Stable identities for the search corpora / collections / indexes the program supports.

Each entry should support:
- stable corpus id
- human-facing name + summary
- storage/posture class:
  - embedded local index
  - remote search cluster
  - vector collection
  - hybrid table/index
  - transient/dev corpus
- source truth pointers:
  - dataset/table refs
  - ingestion source refs
  - schema attachments
- index/runtime refs
- support level
- deprecation / replacement pointers
- optional freshness / rebuild cadence notes

Design rule: keep corpus identity stable across engine moves when possible. Moving an index from Tantivy-in-process to Quickwit or from one vector backend to another should not automatically look like a brand-new feature if the supported retrieval surface did not change.

### 3) `index-profile/v0`
What technical retrieval machinery the surface depends on.

Each profile should capture:
- stable index-profile id
- engine/runtime family
  - tantivy-like full-text
  - quickwit cluster
  - qdrant collection
  - lancedb table/index
  - meilisearch index
  - local ANN library
  - custom
- schema / field mapping posture
- tokenizer / analyzer / normalization refs
- searchable/filterable/facetable/highlightable fields
- vector dimensions / metric / quantization refs when relevant
- persistence / storage / replication posture
- exact vs approximate retrieval notes
- raw config attachments when available

Design rule: preserve raw engine truth as attachments. Do not erase engine-specific knobs into one fake universal index schema.

### 4) `query-surface/v0`
What callers/users are allowed to ask for.

Each query entry should capture:
- stable query-mode id
- linked corpus ids
- query family
- accepted inputs:
  - query string
  - structured filters
  - facet requests
  - vector inputs
  - hybrid inputs
  - paging/sort controls
- supported operators or limitations
- highlight/snippet support
- facet/grouping support
- score visibility / explainability support
- linked ranking profile id
- support level

Design rule: keep caller-visible query capabilities separate from engine internals. A service may support keyword + filters but not expose raw ANN vectors, even if the backend can.

### 5) `ranking-profile/v0`
How candidate generation and ordering are supposed to work.

Each profile should support:
- stable ranking-profile id
- candidate generation mode(s)
- fusion mode:
  - BM25-style only
  - vector only
  - weighted hybrid
  - reciprocal-rank fusion
  - custom reranker
  - multistage prefetch + rescore
- linked tokenizer/embedder/model refs when relevant
- tunable parameter refs
- latency / recall / quality targets if declared
- determinism / stability notes
- known unsupported or unchecked lanes

Design rule: keep ranking posture separate from corpus/index identity. The same corpus may expose multiple supported ranking profiles.

### 6) `retrieval-check-plan/v0`
A plan for validating that the declared retrieval surface still behaves as claimed.

A plan should capture:
- selected corpora/query modes/ranking profiles
- representative query cases
- golden expectations classes:
  - exact document ids
  - allowed result-set windows
  - facet expectations
  - snippet/highlight expectations
  - metric thresholds (MRR/nDCG/Recall@k/latency budget)
  - invariant checks (filter exclusion, tenant isolation, safe-mode behavior)
- environment + dataset snapshot refs
- model/embedder/version refs when relevant
- unsupported/unchecked lanes

Design rule: keep illustrative examples separate from checked cases. Not every example query in docs is test evidence.

### 7) `retrieval-check-report/v0`
Portable results from running the retrieval checks.

A report should capture:
- artifact versions and environment
- corpus/index/ranking ids exercised
- query cases executed
- pass/fail/error outcomes
- result diffs and rank shifts
- metric summaries
- latency summaries
- major incompatibility reason codes, e.g.:
  - `field-no-longer-searchable`
  - `facet-changed`
  - `highlight-changed`
  - `ranking-profile-changed`
  - `hybrid-fusion-changed`
  - `embedder-mismatch`
  - `recall-below-threshold`
  - `latency-budget-regressed`

### 8) `retrieval-pack/v0`
Bundle the retrieval contract and its evidence.

Typical contents:
- `retrieval-surface.json`
- `corpus-profile/*.json`
- `index-profile/*.json`
- `query-surface/*.json`
- `ranking-profile/*.json`
- `retrieval-check-plan.json`
- `retrieval-check-report.json`
- raw attachments:
  - engine configs
  - schema mappings
  - analyzer/tokenizer configs
  - embedder/model metadata refs
  - bounded query fixture sets
  - optional metric dashboards / plots

## UX shape

### `cargo retrievecheck init`
Bootstrap retrieval artifacts from known adapters or a manual scaffold.

### `cargo retrievecheck scan`
Inspect a project and emit a draft inventory:
- known search engines/backends
- likely corpora/indexes
- query endpoints / call sites
- engine config refs
- missing declarations

### `cargo retrievecheck validate`
Validate artifact shapes and cross-links.

### `cargo retrievecheck diff`
Explain retrieval-surface drift between two revisions.

### `cargo retrievecheck run`
Execute selected retrieval checks and emit `retrieval-check-report/v0`.

### `cargo retrievecheck doc`
Generate human-readable retrieval support docs from the declared artifacts.

## Adapters worth targeting first
- Tantivy schema/query/snippet/facet adapters
- Quickwit index-config + doc-mapping + search-settings adapters
- LanceDB corpus/index/query/reranker adapters
- Qdrant collection/query/hybrid-profile adapters
- Meilisearch hybrid/embedder/query-profile adapters
- low-level ANN adapters for `usearch`-style local indexes

## Overlap boundaries
- **Not Dataset Surface Kit:** dataset/table identity and physical-layout truth remain separate attachments; Retrieval Surface Kit consumes them.
- **Not Model Surface Kit:** embedder/tokenizer/model metadata remain separate attachments; Retrieval Surface Kit points at the parts that affect retrieval behavior.
- **Not Service Surface Kit:** HTTP routes remain service-surface artifacts; retrieval artifacts describe the query behavior behind them.
- **Not Schema Contract Kit:** field/value schemas are attachments, not the whole retrieval surface.
- **Not Perf Labs:** performance harnesses remain separate; Retrieval Surface Kit only records the selected latency/quality evidence relevant to support claims.

## Why this is plausible
This proposal does not require one search engine to win.
It only requires the ecosystem to admit that retrieval behavior has become a support surface worth declaring and checking explicitly.

Rust already has enough real pieces:
- full-text libraries,
- search servers,
- vector databases,
- ANN libraries,
- hybrid/rerank patterns,
- and ML-backed retrieval settings.

The missing part is the attachable contract and evidence layer above them.
