# rev0068 — boundary-refined selector/layout audit

This experiment tests the selector bottleneck exposed by rev0065 and rev0066.

Coarse score histograms were quality-safe but over-selected many values. Exact Top-p selected fewer values but exact sorting was expensive. This probe adds a middle path: build the same score histogram, keep all bins above the threshold, and sort only the threshold boundary bin until the target mass is reached.

The benchmark is intentionally fenced:

- local tiny-trained Q/K/V trace only;
- native CPU timing only;
- selector/layout overhead paid inside the timed loop;
- no values or dense outputs are used during selection;
- every deployable path still computes all QK scores;
- not public/pretrained evidence;
- not GPU or fused-kernel evidence.

Run:

```bash
python experiments/trace_packet_boundary_refined_selector/trace_packet_boundary_refined_selector.py
python tools/boundary_refined_selector_audit.py
```
