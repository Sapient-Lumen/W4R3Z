# rev0064 trace packet value-layout envelope

This experiment tests whether the sparse value path was unfairly penalized by the rev0063 mask-scan loop.

It keeps exact Top-p 0.96 support as a non-promotional oracle upper bound, then compares:

- dense value-only accumulation over all tokens;
- sparse mask scan with a branch per token;
- selected-index gather in probability-rank order;
- selected-index gather in sorted key-cache order;
- prepacked selected `(probability, value)` records;
- QK-included sorted/packed oracle paths that still compute every QK score.

The result is a layout envelope, not a selector or kernel claim. Packed selected values are an oracle side input unless a future kernel can build and reuse that layout without erasing the win.
