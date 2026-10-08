# Rev0009 scout notes

## What changed

The hunt shifted from "KV cache tricks" to a broader question: **what role is each memory/compression mechanism playing?** Current candidates separate into answer substrate, router, index, prefetcher, stale-state filter, writable memory, and compute-depth allocator.

## Fresh high-value additions

- **Observability-safe retention**: online memory policies should not leak offline future labels, but they must still pay delayed miss, stale, and reacquisition costs.
- **Latent context compression / LCLM**: compressed context may be most useful as a skim layer that routes to raw expansion.
- **Forecast sparse routing / SparDA**: selection and attention can be decoupled; forecast may be valuable when next-layer support is predictable but current query scores are noisy.
- **Agent context folding / less context**: full history can be worse if stale tool outputs interfere with current state.
- **Depth-recurrent reasoning**: still the best non-cache training candidate for a later tiny-model phase.

## Current best questions

1. What online retention features survive a strict no-offline-leak audit?
2. Is compressed context an answer, router, index, or prefetcher?
3. When does support drift make shared routing fail?
4. Can stale-state interference make full context worse even for exact simulators?
5. Which surprises should directly change next revision priorities?
