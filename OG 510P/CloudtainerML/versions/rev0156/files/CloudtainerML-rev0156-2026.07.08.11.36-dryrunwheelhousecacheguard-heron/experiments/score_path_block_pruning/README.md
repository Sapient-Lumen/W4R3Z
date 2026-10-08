# rev0051 score-path block pruning

This probe attacks a stricter sparse-attention systems question than previous revisions:

> Does the compiler avoid dense QK score computation, or does it only save value reads after all scores have already been computed?

The native C++ benchmark compares three CPU row-attention paths:

1. dense full attention;
2. dense-score mass-histogram sparse attention, which computes every QK score before selecting;
3. block-upper-bound pruning, which computes per-block centroid bounds, opens only blocks whose exact score mass is needed, and certifies a lower bound on retained softmax mass using upper bounds for unopened blocks.

The block-bound path is intentionally conservative. It can win only when key blocks are tight enough and query mass is concentrated. Broad or loose-bound regimes should collapse toward dense computation.
