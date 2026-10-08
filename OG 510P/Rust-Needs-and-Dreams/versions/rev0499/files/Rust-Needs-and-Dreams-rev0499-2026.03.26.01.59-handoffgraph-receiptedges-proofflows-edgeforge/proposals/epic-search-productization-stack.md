# Epic proposal: Search Productization Stack (`cargo search-product`, `search-product-pack/v0`)

## One-line thesis
Build a thin Rust companion layer for **search products** that links **declared retrieval behavior**, **corpus freshness/provenance**, **runtime activation**, **relevance/latency/freshness evidence**, and **support/docs truth** into one portable review boundary without pretending Tantivy, Quickwit, LanceDB, Qdrant, Meilisearch, and model-backed hybrid-search stacks have already converged into one framework or one source of truth.

## Why this is now worth doing
Rust search is no longer just “a few crates if you want them.”
It now has multiple real product lanes:
- embedded/library full-text search,
- remote/distributed index services,
- vector/ANN stores,
- hybrid lexical+semantic retrieval,
- reranking/model-backed search,
- and agent/RAG consumers that depend on those behaviors.

That maturity changes the missing contribution.
The missing thing is **not** another engine or vector DB.
It is the attachable product boundary above them.

## The ecosystem evidence
The current ecosystem already shows the exact fragmentation pattern that calls for a shared product layer:
- Tantivy is a serious library lane and already exposes user-visible snippet/highlight and facet semantics.
- Quickwit’s index config keeps index-uri, doc mapping, indexing settings, and search settings distinct.
- LanceDB now openly describes itself as a search/retrieval layer with vector, full-text, and hybrid search, and documents reranking as part of the story.
- Qdrant’s current hybrid-query docs treat dense+sparse fusion as a first-class operation rather than a custom integration hack.
- Meilisearch’s AI-powered search docs treat embedders, embedder source/model choice, and hybrid/vector search as documented product capabilities.

That is exactly when Rust should add a **thin pack/report/import layer** instead of another winner-take-all pitch.

## What this epic should provide
A thin, portable search-product contract layer with:
- subject identity for the exact app/service/binary/release/deployment being reviewed,
- imported retrieval-surface artifacts,
- imported corpus/data provenance and freshness artifacts,
- imported runtime activation and model/reranker attachments,
- selected observability/relevance/freshness evidence,
- bounded support/docs/release/incident/agent handoffs,
- explicit diff and lossiness reporting between revisions or consumers,
- and no pretense that one engine schema or one query language owns the whole product.

## This epic should not own
- a universal search API,
- a universal query language,
- a hosted search control plane,
- a vector/full-text/hybrid winner declaration,
- a fake one-number “search quality” badge,
- or a reimplementation of existing engines and databases.

## Candidate artifact family

### `search-product-brief/v0`
Why the product exists, intended consumer set, search modes in scope, support levels, freshness budget, and review status.

### `search-product-subject/v0`
The exact service/app/workspace/release/deployment subject, imported retrieval/corpus/runtime/model/support surfaces, comparison base, and environment/support scope.

### `search-product-pack/v0`
The portable review bundle linking:
- imported `retrieval-pack` attachments,
- imported corpus/data freshness attachments,
- imported runtime-settings and optional model/reranker attachments,
- imported observability/evidence artifacts,
- imported support/docs/release/incident handoffs,
- local notes, waivers, caveats, and integrity metadata.

### `search-product-diff/v0`
What changed between two review points, with separate sections for:
- corpora / indexes / collections / source datasets,
- query modes / filters / facets / highlights,
- ranking / reranking / hybrid posture,
- embedder/model attachments,
- freshness / rebuild / import cadence,
- runtime activation / degraded modes,
- docs/support/release claims.

### `search-product-handoff/v0`
Bounded consumer summaries for:
- service/API consumers,
- support / incident review,
- release review,
- atlas / adoption review,
- agent / RAG consumers,
- assistant/editor rendering.

## Recommended rollout
1. query/ranking product lane
2. corpus freshness / rebuild lane
3. hybrid/semantic/model-attachment lane
4. runtime/evidence/fallback lane
5. service/support/release/agent handoff lane

This should be driven by [`design/search-productization-pilot-program.md`](../design/search-productization-pilot-program.md).

## What makes this epic “epic” rather than incremental
A merely incremental tool would improve one lane:
- a nicer Tantivy helper,
- a nicer Quickwit config generator,
- a nicer Qdrant/LanceDB/Meilisearch adapter,
- a nicer embedding/reranker integration,
- or a nicer query dashboard.

An epic contribution here instead gives Rust one **portable search-product contract** above those lanes.
That is strategically different because it can:
- make service/support/release/agent reviews share the same search subject and evidence boundary;
- let full-text, distributed, vector, hybrid, and reranked workflows stay specialized without pretending any one defines the whole product;
- keep query behavior, corpus freshness, runtime activation, evidence, and support claims distinct but linked;
- and give downstream tooling a bounded artifact to import instead of re-scraping engine configs, dashboards, embedder setup, and README prose.

## Design principles
- **Query behavior is not corpus freshness truth.**
- **Corpus freshness is not runtime activation truth.**
- **Hybrid/model attachments are imports, not the whole product.**
- **Observability evidence is not the declaration, and vice versa.**
- **Support/docs truth is not implied by one working demo.**
- **Consumer summaries are intentionally lossy and say so.**
- **The stack stays thin.**

## Success conditions
This epic is succeeding when Rust teams can say:
- “this is the exact search product subject,”
- “these are the corpora/query/ranking semantics we actually support,”
- “these are the data freshness and rebuild assumptions behind that support,”
- “these are the hybrid/model/reranker facts we imported when relevant,”
- “these are the runtime settings and degraded modes that materially changed behavior,”
- “this is the evidence we have for relevance, latency, and freshness,”
- “this is what changed from the prior review,”
- and “this is what service/support/release/agent consumers may safely conclude,”

without inventing a bespoke “search platform readiness” schema for every repository.

## Read this with
- `gaps/search-products-corpora-indexes-ranking-freshness-and-support-contracts.md`
- `design/search-productization-stack.md`
- `design/search-productization-pilot-program.md`
- `design/retrieval-surface-kit.md`
- `design/dataset-surface-kit.md`
- `design/runtime-settings-kit.md`
- `design/observability-kit.md`
- `design/support-envelope-kit.md`
