# rev0013 scout notes — native frontier / cache-object shift

## User-linked paper

`SRC-0210` (`2603.24647`) belongs in CloudtainerML as a **meta-optimization** paper, not as a cache paper. The actionable point is Centaur: classical optimizer state plus occasional domain-prior overrides. For us that means future sweeps should not be random hand grids forever; a stateful optimizer can search probe knobs while we inject hypotheses.

## New research clusters

### 1. Cache object, not just cache policy

`SRC-0201` argues that full KV may be redundant with residual checkpoints. Regardless of whether the full claim survives scrutiny, it forces a better CloudtainerML question: what is the **right object to store**?

Candidates now include full KV, residual checkpoint, hidden state, low-rank adapter delta, compressed latent, fast-weight state, and token stream.

### 2. Move query, not cache

`SRC-0202` is systems-heavy but experimentally useful. Sparse/latent attention makes the query payload small enough that routing queries can beat fetching KV blocks. This is not a training project; it is a phase-boundary/cost-model project.

### 3. Constant-memory write gates

`SRC-0203` says the batch-1 endless-agent regime is different from datacenter serving. If memory write cost matters, we should test gates based on downstream action/value surprise, not just observation novelty.

### 4. Latency-aware exactness

`SRC-0204` makes a clean distinction: exact/lossless cache management can still be optimized, but the objective is latency and recompute cost rather than model accuracy. This belongs as a systems-cost lane.

### 5. Fast-weight edit gates

`SRC-0206` is now connected to Tensor Cache / linear attention: if the memory is a matrix of outer products, editing old associations and writing new ones are different operations. The first native hand-gate toy did **not** prove decoupling helps; it found tied scalar gates stronger in the smoke setup. That is useful negative evidence and suggests trained gates or better oracle construction are needed.

### 6. Taxonomy matters

`SRC-0208` made the object taxonomy urgent. The cube has been mixing token compression, cache eviction, latent communication, adapter memory, hidden-state transfer, and residual recomputation under one umbrella. Rev0013 adds a datacube axis to separate WHAT / HOW / budget.

## New runnable native probes

- `native_token_precision_frontier`: fixed byte budget, more low-bit tokens vs fewer high-bit tokens.
- `residual_stream_kv`: full KV vs residual checkpoint object frontier.
- `query_move_cache_cost`: move query vs move cache vs local recompute.
- `gated_delta_memory`: tied scalar vs decoupled channel erase/write memory.
- `express_streaming_coreset`: carried forward and rerun under rev0013 native audit.

## Current surprises

1. The residual/KV object question is more disruptive than another eviction heuristic.
2. The query-routing cost model makes systems papers actionable even without a GPU cluster.
3. The first decoupled erase/write hand-gate toy was negative: tied scalar won all three regimes. That does **not** refute Gated DeltaNet-2, but it says naive decoupling is not enough.
4. C++ changes the cube’s shape: high-volume adversarial sweeps are now cheap enough to be first-class.
