# rev0052 observable block-index pruning

This experiment follows the rev0051 score-path pruning result, but removes the most dangerous privilege: generator-side block centroids and radii.

The main selector builds centroids and max radii from the observable key cache only, before seeing any query. It then uses those upper bounds to decide which blocks to open. Index build cost is reported separately and amortized over 32 queries.

A sampled-radius variant is included as a negative control. It estimates each block radius from only four tokens, so it can underbound unseen keys. The audit requires those rows to be labeled unsafe and non-promotable.
