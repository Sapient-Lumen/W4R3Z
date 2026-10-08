# Design: Search Productization Pilot Program (Query/Ranking Truth → Corpus Freshness → Hybrid/Model Attachments → Runtime/Evidence → Support/Release Consumers)

## Goal
Turn the **Search Productization Stack** into a ranked execution program so the archive can answer a practical question: what is the first boring, portable, ecosystem-shaping contribution that would materially improve how Rust search products are built, tested, operated, and supported?

The pilot program should not chase a universal engine or hosted search platform.
It should sequence the contribution so each lane proves something concrete before the next lane widens scope.

## Why a pilot program is necessary
Search is unusually vulnerable to fake maturity.
A good demo query, a benchmark graph, a relevance screenshot, or one hybrid-search blog post can hide the actual product questions:
- what corpus the product really covers,
- whether facets/highlights/ranking semantics are part of the promise,
- whether hybrid/vector behavior is really active,
- how stale indexes are allowed to become,
- what degraded modes exist,
- and what support/release consumers may actually conclude.

A credible plan therefore needs to decide:
- when retrieval-surface truth is already enough,
- when corpus freshness/rebuild/import truth must be attached,
- when semantic/hybrid/model facts become part of the contract,
- when runtime/relevance/freshness evidence is required,
- and which release/support/service consumers justify graduation.

## Principles
1. **Start from declared query behavior, not engine ideology**
   - a pack that proves what users may ask and what semantics they may expect is worth more than another backend manifesto.
2. **Keep search behavior, corpus provenance, and runtime activation separate**
   - they travel together in real systems, but they are not the same source of truth.
3. **Support degraded modes honestly**
   - stale indexes, lexical-only fallbacks, disabled rerankers, tenant-safe reduced query modes, and feature-gated semantic search are real product truth.
4. **Freshness is part of the product boundary**
   - corpus lag, indexing cadence, and rebuild/import posture should graduate before big support claims do.
5. **Hybrid/model lanes are imports, not new default truth**
   - semantic embeddings, rerankers, and retrieval models matter, but they should attach to the stack instead of silently becoming the owner of it.
6. **Consumers import; they do not reinterpret**
   - release, support, service, agent, and atlas consumers should import artifacts instead of becoming the hidden truth engine.

## Common artifacts this program should drive
- `search-product-brief/v0` — declares which pilot lane is being exercised, scope, targets, and non-goals.
- `search-surface-brief/v0` — bounded summary of corpora, query families, filter/facet/highlight behavior, ranking profiles, and evidence actually exercised.
- `search-corpus-brief/v0` — corpus/data source identity, freshness/rebuild cadence, source-schema attachments, and stale/degraded posture.
- `search-runtime-brief/v0` — engine/profile/embedder/reranker/cache/tenant/runtime activation summary with links to evidence.
- `search-evidence-brief/v0` — selected relevance, latency, freshness, drift, and fallback evidence with explicit caveats.
- `search-consumer-handoff/v0` — what service/release/support/atlas/agent consumers may conclude and what remains out of scope.
- `search-readiness-scorecard/v0` — not a fake maturity score; a lane-by-lane checklist showing which truths exist and which remain absent.
- `search-product-pack/v0` — attachable summary pack importing the lane artifacts used in a specific pilot.

## Ranked pilot lanes

### 1) Embedded / library full-text lane
**Why first:** it proves the most universal search-product claim with the least deployment coercion.

**Concrete scope**
- declared corpus identity,
- full-text query posture,
- filter/facet/highlight semantics,
- ranking profile identity,
- checked example queries,
- and docs/examples that state the search story honestly.

**Graduation bar**
- a reviewer can tell exactly what the search product supports at the query level without reading engine code.

### 2) Corpus freshness / rebuild / import lane
**Why second:** once query truth is real, the next hidden source of product failure is what data the index actually reflects.

**Concrete scope**
- source dataset/table/document identity,
- index/import/rebuild cadence,
- freshness budgets,
- stale-index/degraded behavior,
- partition/tenant/collection structure,
- and evidence that the product can explain its current corpus posture.

**Graduation bar**
- a reviewer can tell what the search product is indexing, how current it is supposed to be, and what happens when it falls behind.

### 3) Hybrid / semantic / reranker attachment lane
**Why third:** this is where search products now most often blur “demo magic” with actual supported behavior.

**Concrete scope**
- vector / lexical / hybrid mode declarations,
- embedder/reranker/model attachments,
- fusion profile identity,
- score visibility / explainability posture,
- checked query cases that prove hybrid/semantic behavior really ran,
- and explicit fallback when semantic lanes are disabled or unavailable.

**Graduation bar**
- the pack can explain whether semantic/hybrid/reranked search is part of the supported product and what lower-layer facts it imports.

### 4) Runtime / evidence / degraded-mode lane
**Why fourth:** runtime settings and evidence usually determine what users actually experience.

**Concrete scope**
- engine/profile/runtime activation,
- cache/replica/tenant/search-mode toggles,
- latency/relevance/freshness evidence,
- rank-shift and drift attachments,
- fallback/degraded mode reports,
- reproducible runtime configurations for support.

**Graduation bar**
- the pack can explain which activated settings materially changed retrieval behavior and what evidence accompanied that change.

### 5) Service / support / release / agent consumer lane
**Why fifth:** this is where the stack proves it matters beyond demos and internal evaluation.

**Concrete scope**
- service endpoint attachments,
- docs/examples/install/support notes,
- release attachments importing search truth,
- support / incident handoffs,
- agent/RAG/consumer imports of search artifacts rather than hand-written summaries.

**Graduation bar**
- a downstream consumer can answer what search story is actually supported and what evidence shipped with it.

## What to defer
- a universal query language;
- one magical vector/full-text/hybrid abstraction;
- hosted orchestration for indexing and search clusters;
- benchmark theater without product-boundary artifacts;
- policy-first hard gates before the evidence lanes exist.

## Immediate archive consequences
- Treat **Retrieval Surface Kit** as the anchor of a broader search-productization seam rather than an isolated engine contract.
- Treat **Dataset Surface** as the freshness/provenance half of the story instead of letting engines silently absorb it.
- Treat **Runtime Settings + Observability** as activation/evidence lanes that support must import instead of reconstructing from dashboards and issue comments.
- Treat **Support Envelope + DocProof** as downstream import lanes that should consume lower-layer search evidence instead of retelling it.
- Add a specific amnesia resistor so later revisions cannot collapse query/ranking truth, corpus freshness truth, hybrid/model attachments, runtime activation, and support/release conclusions into one fake readiness story.

## Read this together with
- `design/search-productization-stack.md`
- `design/retrieval-surface-kit.md`
- `design/dataset-surface-kit.md`
- `design/runtime-settings-kit.md`
- `design/observability-kit.md`
- `design/support-envelope-kit.md`
- `design/docproof-kit.md`
- `design/service-surface-kit.md`
- `design/model-surface-kit.md`
