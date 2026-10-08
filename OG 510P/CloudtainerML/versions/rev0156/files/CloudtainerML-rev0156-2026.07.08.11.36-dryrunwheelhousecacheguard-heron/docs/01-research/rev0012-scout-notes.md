# rev0013 scout notes — C++ native probes, Express, Centaur, TRACE

## Fresh paper triage

- `2603.24647` belongs as a meta-optimization lane: not a cache paper, but directly relevant to how CloudtainerML should allocate experiments under fixed compute.
- `2606.10944` is a strong native/algorithmic target because streaming causal attention approximation can be tested with generated tensors and compiled loops.
- `2606.11119` strengthens the agentic-budget lane: allocate rollouts to contrast-rich prefixes, not just roots.
- `2606.10935` and `2606.10820` add a decoding-acceleration branch: acceptance policies and joint next-k generation can be toy-tested without a full LLM.

## Result-level notes

- The Express-style C++ surrogate helps on broad/drifting regimes but fails isolated early needles; this makes adversarial retention mandatory.
- The Centaur toy makes the linked HPO paper relevant as a meta-optimizer lane.
- TRACE prefix allocation looks better than root-only allocation in most toy sparse-reward regimes.

## Do not overclaim

The rev0013 probes are synthetic smoke tests, not paper reproductions.
