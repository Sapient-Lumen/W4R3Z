# rev0069 certified support reuse

rev0066 showed that reusing an anchor support can reduce QK work but fails output quality. rev0069 tests the missing conservative repair: allow anchor-support reuse only when an observable Q/K/key-drift upper bound certifies that omitted tokens cannot hold too much target-row attention mass.

This is local native CPU evidence over the tiny trained Q/K/V trace packet. It is not public/pretrained evidence, not GPU/fused-kernel evidence, and not a promoted sparse-attention implementation.

The selector/certificate may use query vectors, key vectors, anchor scores, support indices, key norms, and key drift bounds. It may not use values or dense outputs to decide reuse.
