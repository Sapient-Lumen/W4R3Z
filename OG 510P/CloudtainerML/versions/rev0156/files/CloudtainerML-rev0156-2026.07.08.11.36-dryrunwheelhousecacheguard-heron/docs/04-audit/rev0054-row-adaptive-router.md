# rev0054 row-adaptive router audit note

rev0054 moves from a global sparse compiler toward row routing. The important result is mixed and intentionally non-promotional.

On heldout tiny trained-transformer traces, the calibrated bound-precheck router preserves the attention quality bar and beats dense full attention under equal work units. It does not beat the simpler dense-score histogram baseline under equal units. The break-even analysis says the adaptive route only becomes preferable to histogram if QK score work is weighted much more heavily than value reads.

The block-attempt fallback negative control exposes the cost of a tempting but wasteful strategy: trying block pruning deeply and then falling back to dense scoring. Failed exact block opens are counted, making that route materially worse.

Remaining blockers:

- public/pretrained Q/K/V traces;
- GPU or fused-kernel timing;
- an adaptive router kernel path;
- calibration beyond this tiny trace distribution.
