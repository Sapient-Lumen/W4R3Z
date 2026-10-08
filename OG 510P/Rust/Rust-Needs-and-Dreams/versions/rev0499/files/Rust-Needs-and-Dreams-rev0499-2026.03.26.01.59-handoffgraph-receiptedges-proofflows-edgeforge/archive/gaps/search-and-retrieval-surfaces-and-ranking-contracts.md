# Gap: search and retrieval surfaces and ranking contracts

## What is missing
Rust now has credible building blocks for:
- full-text indexing and query execution,
- faceting, snippets, and field-aware search,
- distributed/object-store-backed search clusters,
- vector similarity search,
- hybrid keyword+semantic retrieval,
- and reranking / multistage retrieval.

What it still lacks is a **boring, reviewable contract** for the supported retrieval surface itself.

Today teams can separately:
- define corpora and indexes,
- expose search endpoints or SDK methods,
- wire tokenizers, fields, filters, and facets,
- add embeddings and hybrid retrieval,
- tune ranking or semantic ratios,
- and sometimes run relevance experiments.

What is still missing is the shared layer that answers:
- what corpus/indexes a program officially supports,
- what query modes and filters it promises,
- what ranking, fusion, highlight, facet, and reranking behavior counts as part of the interface,
- what model/embedder/index/runtime assumptions those claims depend on,
- and what evidence exists that the declared retrieval surface still behaves acceptably.

## Why it matters
Search is no longer a niche subsystem.

It is increasingly a **public support surface** for:
- docs and knowledge bases,
- e-commerce and app navigation,
- logs and traces,
- recommendation and discovery,
- RAG and agent retrieval,
- and internal developer/product workflows where result quality is part of product trust.

Without a shared artifact layer, those truths get scattered across:
- ad hoc index config files,
- route handlers and SDK methods,
- ANN/vector-db collections,
- ranking code and environment variables,
- dashboard screenshots,
- notebooks,
- benchmark scripts,
- and tribal memory about which filters, fields, or rerankers are “safe” to depend on.

That is exactly the pattern this archive keeps surfacing: strong point tools, weak portable artifacts.

## Existing building blocks worth composing
- `tantivy` is explicitly a search engine library — “Think Lucene, but in Rust” — with schema-driven indexing and searching.
  https://docs.rs/tantivy/latest/tantivy/
- Tantivy already has first-class snippet/highlight generation and hierarchical facets, which is important because highlights and facet semantics are part of the user-visible retrieval surface.
  https://docs.rs/tantivy/latest/tantivy/snippet/index.html
  https://docs.rs/tantivy/latest/tantivy/schema/struct.Facet.html
- Quickwit’s index configuration already separates index URI, doc mapping, indexing settings, and search settings such as `default_search_fields`; that is strong evidence that retrieval support needs explicit declarative metadata.
  https://quickwit.io/docs/configuration/index-config
- Quickwit also makes schema posture explicit: fixed-schema, schemaless, or mixed indexing are real support differences, not invisible implementation details.
  https://quickwit.io/docs/overview/concepts/indexing
- LanceDB explicitly positions itself for search/retrieval applications, including vector search, full-text search, and hybrid search with secondary indexes.
  https://docs.lancedb.com/
- LanceDB’s hybrid-search docs and Rust reranker interface make it explicit that hybrid retrieval and reranking are first-class behaviors rather than private implementation details.
  https://docs.lancedb.com/search/hybrid-search
  https://docs.rs/lancedb/latest/lancedb/rerankers/trait.Reranker.html
- Qdrant already has a serious Rust client and explicit support for hybrid and multistage queries, including prefetch + rescore flows.
  https://docs.rs/qdrant-client/latest/qdrant_client/
  https://qdrant.tech/documentation/concepts/hybrid-queries/
- Meilisearch now treats hybrid/full-text/semantic search and embedder configuration as product-level supported behavior, which is a strong signal that retrieval surfaces increasingly include semantic knobs and model assumptions.
  https://www.meilisearch.com/solutions/hybrid-search
  https://www.meilisearch.com/docs/learn/ai_powered_search/getting_started_with_ai_search
- `usearch` shows the lower-level ANN/index lane is also active in Rust: metrics, dimensions, search parameters, persistence, and memory usage are already exposed directly.
  https://docs.rs/usearch/latest/usearch/struct.Index.html

## Why existing tools are not yet the whole answer
The ecosystem has **engines, databases, libraries, and query APIs**, but not the **shared contract / capability / evidence layer**:
- Tantivy helps build full-text search,
- Quickwit helps run large search systems,
- LanceDB/Qdrant/Meilisearch help with vector and hybrid retrieval,
- `usearch` helps with ANN primitives,
- and app teams layer evaluation and product behavior on top.

But teams still have to invent their own answers for:
- stable corpus/index identities,
- normalized query-surface declarations,
- filter/facet/highlight support truth,
- explicit ranking/fusion/reranker metadata,
- distinctions between illustrative queries and checked retrieval cases,
- and diffable review artifacts when a field stops being searchable, a reranker changes, a semantic ratio shifts, or an index moves from exact/full-text to ANN/hybrid assumptions.

This is the same pattern seen elsewhere in the archive: strong execution engines, weak attachable artifacts.

## Target outcome
A project should be able to say:
- “these are the corpora/indexes we officially support,”
- “these are the query/filter/facet/highlight modes users can rely on,”
- “these are the ranking, fusion, embedding, and reranking assumptions behind those results,”
- “these are the relevant latency/recall/quality support envelopes and known unchecked lanes,”
- and “this is the portable bundle CI, release review, operators, product owners, and later archaeology can consume.”

That is bigger than one search crate and smaller than a hosted search platform.
