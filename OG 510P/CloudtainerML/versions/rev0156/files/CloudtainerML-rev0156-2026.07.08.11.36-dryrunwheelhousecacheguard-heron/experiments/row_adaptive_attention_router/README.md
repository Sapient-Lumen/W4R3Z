# rev0054 row-adaptive attention router

This experiment addresses the risk exposed by rev0053: observable block bounds can skip QK score work on some learned rows, but high-support rows collapse toward dense work. A global sparse path is therefore the wrong systems object.

The rev0054 router calibrates simple thresholds on calibration rows, then evaluates heldout rows. It can route to:

- dense full attention;
- dense-score mass histogram, which saves V reads but computes every QK score;
- PCA-sorted observable block-bound pruning, which can skip QK scores when block upper bounds are tight.

The benchmark also includes an aggressive block-attempt fallback path. That path is intentionally included as a negative control because it opens exact block scores before falling back, and the failed-probe overhead must be charged.

This is tiny trained-model CPU/proxy evidence only. It is not public/pretrained evidence and not a GPU or fused-kernel claim.
