# rev0065 deployable selector-layout overhead audit

rev0064 established a layout-positive oracle envelope: selected-index and prepacked selected-value layouts can beat dense value accumulation when exact Top-p support and/or packed records are supplied as side inputs.

rev0065 pays the missing costs. The native replay constructs support from Q/K-derived scores and softmax probabilities inside the timed loop, then builds either a selected-index or packed selected-value layout per query. Selectors are score-only and cannot use values, dense outputs, labels, or oracle support lists.

The result is a useful negative correction: quality remains high, but selector/layout overhead consumes the rev0064 value-layout headroom on the local CPU trace. Histogram selection overselects substantially, exact-sort Top-p selects fewer values but is much slower, and every path still computes all QK scores. The lane therefore remains blocked until a cheaper selector, score-path pruning, GPU/fused kernel path, or public/pretrained trace result changes the evidence.
