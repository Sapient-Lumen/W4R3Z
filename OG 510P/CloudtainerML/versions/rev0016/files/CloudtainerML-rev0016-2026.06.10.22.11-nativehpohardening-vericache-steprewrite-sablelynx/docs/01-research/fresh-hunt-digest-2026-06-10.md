# Fresh hunt digest — 2026-06-10

## What looks newly hot

1. **Decode-time KV cache behavior**: several papers argue that long generated reasoning traces stress the cache differently from static long-input tests. This makes pseudo-decode experiments attractive.
2. **Learning to forget**: cache eviction is shifting from hand-designed scoring to learned retention, RL, and future-utility prediction.
3. **Cache as state**: one intriguing direction treats K/V tensors as a representation for reasoning/sampling control rather than only as an inference acceleration artifact.
4. **Constant-memory recall**: spectral/Koopman and linear-attention papers attack the content-addressed recall cliff directly.
5. **Hybrids everywhere**: score-level fusion, sequence-axis switching, attention/recurrent shared representations, and dynamic local preconditioning all try to avoid a pure attention vs pure recurrence binary.
6. **Mechanistic tiny science**: RASP decompilation, attractor basins, exact state tracking, and grokking geometry all provide small exact tasks where failure modes can be inspected.

## Current taste

The best early CloudtainerML cells are those that can produce phase diagrams without needing a large pretrained model.
