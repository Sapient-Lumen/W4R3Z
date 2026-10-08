# Writable and test-time memory lane

Core sources: `SRC-0027` through `SRC-0038`.

## Competing write mechanisms

- gradient-written prefix slots;
- surprise-gated neural memory;
- batch/past-token optimized memory;
- fixed-size compressed K/V slots;
- growable block-recurrent means;
- fast-weight / adapter updates;
- two-rate consolidation: slow gist plus fast episodic memory.

## Main tiny question

At the same memory budget, which write rule preserves key-value facts, corrections, and multi-hop dependencies best?

## Baselines required

- full attention oracle;
- sliding window;
- reservoir/ring buffer;
- top-attention/top-novelty retention;
- simple learned linear memory.
