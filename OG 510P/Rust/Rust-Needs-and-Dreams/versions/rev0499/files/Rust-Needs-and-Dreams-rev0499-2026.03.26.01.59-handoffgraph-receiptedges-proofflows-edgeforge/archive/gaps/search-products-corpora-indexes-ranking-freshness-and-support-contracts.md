# Gap: search products need corpus, ranking, freshness, and support contracts

## What is missing
Rust now has strong search ingredients, but it still lacks a **boring, end-to-end contract workflow** for search products.

Today teams can separately:
- use Tantivy-style embedded full-text search,
- run Quickwit-style remote/distributed indexes,
- use LanceDB/Qdrant-style vector and hybrid retrieval,
- use Meilisearch-style product search with AI-powered or hybrid modes,
- and wire those results into services, agents, or applications.

What is still missing is the shared layer that answers:
- what corpus or collection the product is claiming to search,
- which query modes / filters / facets / highlights / ranking profiles are actually supported,
- how fresh the indexed data is expected to be,
- what runtime settings, rerankers, or embedders materially change behavior,
- what degraded or fallback modes exist,
- and what support/release/incident consumers can later import without reverse-engineering configs and dashboards.

## Why it matters
This is not the same problem as generic service APIs or model packaging.

For many Rust search applications, the dangerous questions are not only “does the query return something?” but:
- what exact corpus was searched,
- whether a lexical-only or stale-index fallback was silently activated,
- whether facet/highlight behavior is part of the product or just an implementation detail,
- whether hybrid/semantic/reranked behavior really ran,
- and whether support can explain what changed between two revisions.

Today those answers are usually split across engine configs, index-building jobs, embedder settings, runtime env vars, dashboards, and maintainer memory.

## Existing building blocks worth composing
- Tantivy positions itself as a Rust search engine library, and its docs already expose snippet/highlight behavior and facet types as real user-visible semantics.
  https://docs.rs/tantivy/latest/tantivy/
  https://docs.rs/tantivy/latest/tantivy/snippet/index.html
  https://docs.rs/tantivy/latest/tantivy/schema/struct.Facet.html
- Quickwit’s current index configuration already separates index storage location, doc mapping, indexing settings, and search settings like `default_search_fields`.
  https://quickwit.io/docs/configuration/index-config
- Quickwit’s indexing docs explicitly distinguish fixed-schema, schemaless, and mixed indexing modes.
  https://quickwit.io/docs/overview/concepts/indexing
- LanceDB now explicitly positions itself for search/retrieval applications and documents vector, full-text, and hybrid search with secondary indexes.
  https://docs.lancedb.com/
- LanceDB hybrid search also explicitly treats reranking as part of the product surface.
  https://docs.lancedb.com/search/hybrid-search
- Qdrant’s hybrid-query docs explicitly support fusing dense and sparse results via server-side fusion operations like RRF/DBSF.
  https://qdrant.tech/documentation/concepts/hybrid-queries/
- Meilisearch now documents AI-powered search as a normal capability with explicit embedder source/model configuration.
  https://www.meilisearch.com/docs/learn/ai_powered_search/getting_started_with_ai_search

## Why existing tools are not yet the whole answer
The ecosystem has **real search point tools**, but not the **shared contract / diff / evidence layer**:
- Tantivy owns one embedded full-text lane.
- Quickwit owns one cloud/distributed index lane.
- LanceDB and Qdrant own different vector/hybrid lanes.
- Meilisearch owns one product-search lane with AI search built in.

Teams still have to invent their own answers for:
- stable corpus identities,
- freshness budgets and stale-index reason codes,
- portable declarations of query/ranking semantics,
- diffable hybrid/model attachment posture,
- runtime/fallback evidence that survives beyond local dashboards,
- and consumer handoffs for release, support, service APIs, or agent/RAG systems.

## Target outcome
A project should be able to say:
- “this is the search product surface this crate/app/service expects,”
- “these are the corpora/query modes/ranking profiles/freshness assumptions that justify the claim,”
- “these are the runtime activations and degraded modes that materially changed behavior,”
- and “this is the portable bundle release/support/agent/service tooling can consume later.”

That would be a worthy contribution because it would make Rust search products feel less like bespoke glue and more like reviewable systems.
