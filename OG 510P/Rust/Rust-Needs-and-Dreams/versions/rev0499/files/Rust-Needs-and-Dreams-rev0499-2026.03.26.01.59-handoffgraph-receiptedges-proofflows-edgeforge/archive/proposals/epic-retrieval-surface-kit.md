# Epic proposal: Retrieval Surface Kit

## Thesis
Rust’s search/retrieval ecosystem is mature enough that the missing contribution is no longer “yet another search crate,” “yet another vector database client,” or “yet another RAG demo wrapper.”
The higher-leverage missing piece is a **portable retrieval-surface contract** that lets teams declare, diff, validate, and ship what a search/retrieval interface actually promises: corpus identity, query modes, filter/facet/highlight behavior, ranking or hybrid posture, model/embedder dependencies, and checked retrieval evidence.

In other words: Rust needs a boring, attachable `retrieval-pack/v0` more than it needs one more engine pretending interoperability and quality review are already solved.

## Why now
The ecosystem signals line up:
- Tantivy is already a serious full-text library in Rust.
- Quickwit already turns Rust search infrastructure into cloud/object-store-scale systems with explicit index/search settings.
- LanceDB, Qdrant, and Meilisearch now make hybrid/semantic retrieval normal rather than exotic.
- Lower-level ANN/search-index work like `usearch` is also active in Rust.
- The hard part is increasingly not “can Rust run retrieval?” but “what exactly does this retrieval surface promise, under what ranking/model/index assumptions, and what was actually checked?”

Sources:
- https://docs.rs/tantivy/latest/tantivy/
- https://docs.rs/tantivy/latest/tantivy/snippet/index.html
- https://docs.rs/tantivy/latest/tantivy/schema/struct.Facet.html
- https://quickwit.io/docs/configuration/index-config
- https://quickwit.io/docs/overview/concepts/indexing
- https://docs.lancedb.com/
- https://docs.lancedb.com/search/hybrid-search
- https://docs.rs/lancedb/latest/lancedb/rerankers/trait.Reranker.html
- https://docs.rs/qdrant-client/latest/qdrant_client/
- https://qdrant.tech/documentation/concepts/hybrid-queries/
- https://www.meilisearch.com/solutions/hybrid-search
- https://www.meilisearch.com/docs/learn/ai_powered_search/getting_started_with_ai_search
- https://docs.rs/usearch/latest/usearch/struct.Index.html

## What should be built
A first credible version should ship:
1. `retrieval-surface/v0`, `corpus-profile/v0`, `index-profile/v0`, `query-surface/v0`, `ranking-profile/v0`, `retrieval-check-plan/v0`, `retrieval-check-report/v0`, optional `retrieval-diff-report/v0`, and `retrieval-pack/v0`
2. adapters for common Rust retrieval lanes (Tantivy, Quickwit, LanceDB, Qdrant, Meilisearch, local ANN indexes)
3. docs/reference generation for declared corpora, query modes, filter/facet/highlight support, and ranking/hybrid assumptions
4. validation/reporting support for retrieval-surface drift, ranking/fusion changes, quality regressions, and checked-vs-illustrative query separation
5. examples showing retrieval packs attached to API releases, docs search, internal search services, commerce/search UX, and RAG/recommendation workflows

The winning version is boring, adapter-heavy, and explicit about what it does **not** own.
It should make today’s pieces legible together rather than replacing them.

## Initial pilots
- one local Tantivy pilot that proves snippets, facets, and searchable-field posture belong in the contract
- one Quickwit pilot where schema/index/search settings and support claims stay attached across cluster/environment changes
- one LanceDB pilot that proves hybrid retrieval + reranker behavior belongs in the surface declaration
- one Qdrant pilot for multistage/prefetch + rescore retrieval profiles
- one Meilisearch pilot where semantic ratio/embedder assumptions are explicit rather than hidden in deployment state

## Milestones
1. **v0 artifacts + docs**
   - publish schemas and examples
   - preserve corpus identity, query surface, and ranking posture as separate artifacts
2. **v0.2 adapters**
   - support Tantivy, Quickwit, LanceDB, Qdrant, Meilisearch, and one lower-level ANN adapter
3. **v0.3 cross-kit integration**
   - integrate with Service Surface, Model Surface, Dataset Surface, Runtime Settings, Support Envelope, and Perf Labs workflows
4. **v1 ecosystem pilots**
   - at least three materially different adopters use the schemas without sharing one exact retrieval engine or hosting model

## Success metrics
- Teams can review search/retrieval changes as explicit artifacts instead of route diffs, config snippets, notebooks, and screenshots.
- Query/filter/facet/highlight support becomes more honest because supported subsets and unchecked lanes are explicit.
- Hybrid/semantic ranking changes become reviewable rather than silent behavior drift.
- Retrieval quality evidence becomes attachable to releases and migrations instead of living only in bespoke eval code.
- Rust retrieval systems become easier to hand off across teams because supported search behavior is no longer tribal knowledge.

## Archive fit
This proposal fills a real gap between several existing concise-archive kits:
- Dataset Surface Kit covers dataset/table support,
- Model Surface Kit covers model/tokenizer/runtime packaging,
- Service Surface Kit covers HTTP route and middleware behavior,
- Schema Contract Kit covers raw machine-readable schemas,
- and Perf Labs covers performance evidence.

But none of those is the portable contract for the **retrieval/search boundary itself**.
Retrieval Surface Kit is the missing substrate that keeps corpora, query modes, ranking/hybrid behavior, and checked retrieval evidence attached to one reviewable interface without absorbing the rest of the stack into one mega-format.
