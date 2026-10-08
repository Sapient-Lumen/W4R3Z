# Design note: Search Productization Stack (Retrieval Surface + Dataset Surface + Runtime Settings + Observability + Support Envelope)

## Goal
Define the **division of labor and consumer flow** between Rust search/retrieval surfaces, corpus/data provenance, runtime activation, observability/relevance evidence, and support/docs claims so the ecosystem can make **search products** reviewable without anointing one engine, one vector database, one reranker, or one “AI search” stack as the winner.

This is **not** another search engine or vector database.
It is a stack note explaining how existing archive pieces should compose:
- [`design/retrieval-surface-kit.md`](./retrieval-surface-kit.md)
- [`design/dataset-surface-kit.md`](./dataset-surface-kit.md)
- [`design/runtime-settings-kit.md`](./runtime-settings-kit.md)
- [`design/observability-kit.md`](./observability-kit.md)
- [`design/support-envelope-kit.md`](./support-envelope-kit.md)
- [`design/docproof-kit.md`](./docproof-kit.md)
- [`design/service-surface-kit.md`](./service-surface-kit.md)
- [`design/model-surface-kit.md`](./model-surface-kit.md)
- [`design/schema-contract-kit.md`](./schema-contract-kit.md)
- [`design/release-truth-stack.md`](./release-truth-stack.md)

## Why this note is needed now
Rust’s current search signals no longer say only “you can build search in Rust.” They say Rust already has **serious but non-equivalent search product lanes**, and that the missing contribution is the product boundary above them:
- Tantivy is still an intentionally low-level search-engine library, but it already exposes user-visible snippet/highlight behavior and facet semantics. That means search result presentation is part of the supported surface, not just backend trivia.
- Quickwit’s index configuration explicitly separates index storage, document mapping, indexing settings, and search settings like `default_search_fields`, and current Quickwit docs also keep fixed-schema, schemaless, and mixed indexing modes distinct. That is a strong signal that index and search behavior already need declarative product truth.
- LanceDB now openly positions itself for search/retrieval applications and says it supports vector search, full-text search, and hybrid search with secondary indexes. Its hybrid-search docs also treat reranking as a first-class lane, with built-in and custom rerankers.
- Qdrant’s current hybrid-query docs make dense+sparse fusion an explicit feature, including RRF/DBSF-style fusion over prefetched results. That means the “search product” story increasingly spans multiple representations of the same corpus rather than one index flavor.
- Meilisearch now treats AI-powered search as a normal product capability: embedder configuration, embedder source/model choice, and hybrid/vector retrieval are all documented as supported behaviors rather than hidden implementation details.
- The 2025 State of Rust survey still says online documentation is the preferred canonical reference while debugging and resource usage remain major productivity pain points. That increases the value of machine-usable search-product artifacts over README folklore and dashboard screenshots.

Together those signals justify treating search shipping quality as a **frontier-worthy productization seam** instead of leaving Rust search split across index configs, embedder setup, ranking glue, service docs, issue threads, and ad hoc support notes.

## Stack layers

### 1) Retrieval Surface: declared search behavior truth
Retrieval Surface owns the **declared search boundary**:
- corpora/indexes/collections in scope,
- query families,
- filters/facets/highlights,
- ranking and reranking profiles,
- hybrid/vector/full-text posture,
- and checked retrieval evidence.

This layer answers questions like:
- “Which query capabilities are actually part of the product?”
- “Which facets/highlights/groupings are stable enough for support and docs?”
- “Which ranking profiles are first-class versus experimental?”

Design rule: **query/ranking semantics stay separate from corpus provenance, runtime activation, and support claims**.

### 2) Dataset Surface: corpus provenance, freshness, and rebuild truth
Dataset Surface owns the **content side of the search promise**:
- source datasets/tables/documents,
- indexing/import provenance,
- freshness and rebuild cadence,
- chunking/partitioning/layout assumptions,
- tenant or collection partition truth,
- and source-schema attachments when relevant.

This layer answers questions like:
- “What corpus does this search product actually cover?”
- “How stale can the index be before the support claim changes?”
- “Which reindex/rebuild/import assumptions matter to result quality?”

Design rule: **corpus/data truth must not be flattened into one engine-specific index description**.

### 3) Runtime Settings: activation and live-mode truth
Runtime Settings owns the **live activation boundary**:
- embedded versus remote engine choice,
- index/profile/embedder selection,
- reranker or hybrid-fusion activation,
- cache/replica/tenant/runtime knobs,
- safe-mode or degraded fallback posture,
- and environment/secret/config attachments that materially change retrieval behavior.

This layer answers questions like:
- “Which settings changed what the product searched or how it ranked?”
- “Was semantic/hybrid behavior actually active?”
- “Which runtime knobs are required for the documented product mode?”

Design rule: **runtime activation must not live only in deploy scripts, env-var docs, or operator memory**.

### 4) Observability: relevance, latency, freshness, and failure evidence
Observability owns the **evidence layer**:
- query latency and error classes,
- relevance/quality metrics,
- rank-shift and drift evidence,
- index freshness / backfill / lag reports,
- fallback/degraded-mode evidence,
- and diagnostic traces that explain what search path was taken.

This layer answers questions like:
- “What evidence exists that the advertised search modes still behave acceptably?”
- “Did a result change because the ranking changed, the data changed, or the runtime settings changed?”
- “When did the product fall back to stale/no-semantic/no-hybrid behavior?”

Design rule: **perf/relevance/freshness evidence must stay separate from the declared product surface, even when support imports both**.

### 5) Support Envelope + DocProof: shipped promise truth
Support Envelope and DocProof own the **what is actually promised** boundary:
- supported engines/modes/backends,
- supported corpus freshness windows,
- supported full-text/vector/hybrid/rerank combinations,
- known degraded/fallback lanes,
- checked docs/examples/snippets,
- and release/support attachments that explain what search story actually shipped.

This layer answers questions like:
- “Which search features are supported, best-effort, or experimental?”
- “What may release/support/docs consumers legitimately conclude?”
- “What is documented but not yet evidenced, and vice versa?”

Design rule: **a demo query, dashboard, or benchmark is not the support contract**.

### 6) Downstream consumers and imports
The stack becomes ecosystem-worthy when real consumers can import it without flattening it:
- **Service Surface** consumers can attach HTTP/RPC endpoint truth without redefining search behavior;
- **Model Surface** consumers can attach embedder/reranker/tokenizer truth when semantic search is involved;
- **Schema Contract** consumers can attach result payload and filter-schema truth;
- **Identity Surface** consumers can attach tenant/auth/query-scope truth;
- **Release / incident / support / atlas / agent** consumers can import selected search-product evidence instead of reverse-engineering configs and dashboards.

Design rule: **consumers import selected evidence; they do not become the hidden source of truth for search semantics**.

## What an epic contribution should look like in practice
A worthy contribution here is not “build the one true Rust search platform.”
It is a portable, reviewable stack with explicit boundaries:

1. **search-surface truth first**
   - prove corpora/query modes/filter/facet/highlight/ranking semantics on one real subject;
2. **corpus freshness + rebuild/import truth second**
   - make source-data identity, indexing cadence, and stale-index posture explicit;
3. **semantic/hybrid/model attachments third**
   - attach embedder/reranker/model facts without flattening them into generic search truth;
4. **runtime/evidence truth fourth**
   - make engine choice, runtime activation, relevance/latency/freshness evidence, and degraded modes explicit;
5. **service/support/release consumers fifth**
   - prove that release notes, support docs, service APIs, and agent/RAG consumers can import the artifacts honestly.

An eventual aggregate artifact may exist, but it should be a **thin referenced pack** such as `search-product-pack/v0`, not a new mega-framework.

## Non-goals
- not a universal search engine API;
- not a vector-database winner declaration;
- not a RAG framework or agent wrapper;
- not a relevance dashboard that becomes the hidden truth engine;
- not a hosted control plane for indexing/reindexing;
- not a fake one-number “search readiness” score.

## Archive implications
- The archive should now treat **Retrieval Surface + Dataset Surface + Runtime Settings + Observability + Support Envelope** as a coupled **Search Productization Stack** in frontier discussions.
- Future revisions should prefer **query/ranking truth, corpus freshness truth, semantic/hybrid attachments, runtime activation, evidence, and shipped/support truth** over another engine bake-off, vector DB wrapper, reranker helper, or product-marketing demo.
- When Agent, Model, Service, Schema, Identity, Release, Support, or Documentation work cites search readiness, they should import **search-surface truth**, **corpus freshness truth**, **runtime truth**, **relevance/freshness evidence**, and **support truth** separately.

## References (signals)
- 2025 State of Rust survey:
  https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- Retrieval/search engine signals:
  https://docs.rs/tantivy/latest/tantivy/
  https://docs.rs/tantivy/latest/tantivy/snippet/index.html
  https://docs.rs/tantivy/latest/tantivy/schema/struct.Facet.html
  https://quickwit.io/docs/configuration/index-config
  https://quickwit.io/docs/overview/concepts/indexing
  https://docs.lancedb.com/
  https://docs.lancedb.com/search/hybrid-search
  https://qdrant.tech/documentation/concepts/hybrid-queries/
  https://www.meilisearch.com/docs/learn/ai_powered_search/getting_started_with_ai_search
