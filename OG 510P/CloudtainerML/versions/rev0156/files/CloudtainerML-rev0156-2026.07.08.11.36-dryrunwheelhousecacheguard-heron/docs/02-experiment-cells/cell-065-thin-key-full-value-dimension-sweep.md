# CELL-065 — Thin-Key / Full-Value Dimension Sweep

Priority: P1
Status: candidate
Sources: SRC-0117, SRC-0097, SRC-0106

Question: How few key dimensions are enough for selection if values carry rich information?

Cheap first run: Compress key dimension while preserving full values on support-sensitive tasks.

Baselines: full keys/full values, random projected keys, SVD keys, shared+low-rank key residuals

Metrics: support recall, attention KL, output MSE, key-cache bytes

Stop condition: If support recall collapses before meaningful key savings, find hard floor.
