# rev0065 deployable selector-layout overhead replay

rev0064 showed that selected-index and prepacked value layouts can make sparse value accumulation faster, but the selected support and packed records were supplied as oracle side inputs. This experiment pays the selector and layout construction inside the native loop.

It compares dense QK attention against score-only selectors that use Q/K-derived scores and softmax probabilities only:

- histogram mass selector with selected-index gather;
- histogram mass selector with per-query packed selected values;
- exact-sort Top-p selector with selected-index gather;
- exact-sort Top-p selector with per-query packed selected values.

The experiment remains local CPU evidence over the tiny trained Q/K/V packet. It is not public/pretrained evidence, not GPU timing, and not a fused-kernel claim.
