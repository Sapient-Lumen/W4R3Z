# Changelog

## rev0013 — nativefrontier-querymove-residualgate-onyxlynx

- Expanded C++ from one native probe to five compiled source-only probes.
- Added native token-precision frontier probe.
- Added residual-stream/KV cache object frontier probe.
- Added move-query-vs-move-cache systems cost model.
- Added decoupled erase/write fast-weight memory probe; first smoke result is negative for naive decoupling.
- Re-ran Express, Centaur HPO, TRACE prefix rollout, and CLP acceptance under rev0013 outputs.
- Added sources around residual cache objects, cross-instance query routing, AURA, AsymCache, Entropy Gate, Gated DeltaNet-2, Exact Linear Attention, latent communication, LRKV, and autoresearch/Centaur.
- Refactored the native audit to compile all C++ probes in a temp directory and reject checked-in binaries.
- Updated baby datacube axes around memory object, transport/compute operation, failure mode, implementation tier, and budget.

# rev0011 — entropy/rksc/agent-search/report-refactor

- Added runnable probes for entropy-guided head/segment budget allocation, reasoning branch cache sharing plus early exit, and agentic DFS/backtracking search.
- Added fresh sources for EntropyInfer, Agentic Transformers, STaR-KV, Exact Linear Attention, FlashCP, and context-intensive KV offloading.
- Added traceability audit to connect sources -> ideas -> cells -> notes/probes.
- Reconsidered priorities: do not escalate to baby LM yet; choose one tiny trained model only after symbolic probes separate.

# Changelog

## rev0008 — pcafintent-routeraudit-latenthist-jasperlynx

- Added five runnable probes: PCAF sparse memory, IntentKV pruning, shared routing once, HIST sliding-window order, and latent/explicit router.
- Added `tools/probe_metric_index.py` and dashboard artifacts for primary-metric readiness.
- Added 15 new experiment cells and 22 open questions.
- Reconsidered priorities: cache/memory remains backbone, latent-compute routing promoted, audit/schema refactor becomes P0.
- Kept retired side-lanes absent.

## Added

- New source, idea, question, and cell entries through `SRC-0129`, `IDEA-0074`, `Q-0128`, and `CELL-074`.
- Runnable hierarchical FadeMem-style cache probe and smoke output.
- Runnable / retained rev0006 probes for value banks, blurry-window memory, branch cache sharing, and attention runtime termination.
- Probe dashboard, probe-suite dashboard, and cube audit tools.

## Refactored

- Root porch docs now point to dashboard/audit surfaces.
- Baby datacube candidate now emphasizes memory form, reuse scope, failure mode, and budget axes.
- Smoke validation now checks current dashboard/audit/probe paths and stale manifest hashes.

## Still open

- Probe JSON schemas remain heterogeneous; the dashboard records this rather than hiding it.
- No final tiny model architecture has been selected.

## rev0007 — 2026-06-10T03:25:00-04:00

Codename: `reasonwave-tokenprecision-amnesiaprobes-steellynx`

- Removed nothing from active lanes; retired side-lanes remain absent.
- Added 23 research sources around ReasonAlloc, Attention Amnesia, FlashMemory, shared sparse routing, range-search KV indexing, QK restoration, low-rank KV variants, one-bit SSMs, state tracking, and circuit telemetry.
- Added runnable probes for token-vs-precision budget, Reasoning Wave budget allocation, and QK restore amnesia.
- Promoted CELL-072 to P0 runnable. Added CELL-075 through CELL-090.
- Refactored dashboards/audit tools toward revision-aware output names.
- Regenerated source/idea/question/cell registries and validation surfaces.


## rev0009 — 2026-06-10T13:31:00-04:00

- Added `SURPRISE-LEDGER.md/json` and `tools/surprise_audit.py`.
- Added runnable probes for observability-safe retention, latent context compression, and forecast sparse routing.
- Added `tools/cache_probe_report.py` as a family-level comparison/refactor surface.
- Added fresh sources around SparDA, OSL-MR, ActiveMem, Latent Memory, HIPIF, context engineering, GBLA, and depth-recurrent transformers.
- Added 14 experiment cells and updated the baby datacube candidate with a `mechanism_role` axis.
- Reconsidered priorities toward delayed costs, compression roles, and surprise-driven steering.

## rev0010 — 2026-06-10 14:08 ET — easestill-loramem-smtschema-ravenlynx

- Added four runnable probes: EASE-style evidence-aligned query adaptation, parametric/KV memory crossover, Still-style single-pass latent compaction, and SMT-style supervised transition labels.
- Added `tools/primary_metric_patcher.py` and `tools/probe_graph_specs.py` as audit/refactor infrastructure.
- Patched older probe artifacts with `summary.primary_metric` annotations; row data unchanged.
- Added sources and cells around EASE-TTT, Still, Semantic Cache Distillation, planning-aligned compression, pretraining grokking, Low-Rank Decay, SparseX, and supervised memory training.
- Reconsidered priorities around mechanism roles: query supervision, parametric prior, latent compactor, segment reuse, transition-label teacher, and stale-state filter.

## rev0014 — nativephase-lrkv-santa-kvcat-ivorylynx

- Added five native C++ probes: residual/KV sensitivity, query-move phase boundary, LRKV head diversity, stochastic sparse attention, and KV-CAT compressibility.
- Refactored native audit to enforce output revision and primary-metric schema.
- Added native family report.
- Deduped duplicate LRKV and Gated DeltaNet-2 source rows.
- Added sources/ideas/questions/cells for Vortex, SANTA, TokenMizer, Gist Sparse Attention, conversation-level scheduling, and HybridKV.


## rev0015 — nativehpo-hypermemory-sycophancy-dfssm-graphitelynx

- Added four native C++ probes.
- Added new June 2026 research sources around hypergraph memory, DF-SSM, memory sycophancy, LongFlow, KATE, GASLoC, future steering, prompt learning, and quantization scales.
- Added native probe index and refactored smoke validation.
- Reconsidered priorities toward memory-object choice and native phase diagrams.

## rev0016

- Added C++ VeriCache guard wind tunnel.
- Added C++ periodic / reasoning-step cache rewrite probe.
- Added C++ persistent-memory provenance phase sweep.
- Added native hardening dashboard/report.
- Added fresh source/idea/question/cell material around verified cache recovery, fixed tensor memory, cached state representations, and gated history recall.
