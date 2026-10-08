# rev0032 scout notes

Focus: trained tiny escalation plus fresh performance-core scouting.

New sources promoted:

- `SRC-0336` — On Subquadratic Architectures: state tracking/correction, xLSTM vs Mamba-2 vs Gated DeltaNet.
- `SRC-0337` — Attention by Synchronization: no-exp/physical-substrate attention as a cost-regime question.
- `SRC-0338` — Chain of Operators: explicit operator harnessing as a possible analogy to simple residual operator pairs.
- `SRC-0339` — Frequent Directions bandit: streaming sketching as a future memory/compression primitive.
- `SRC-0340` — Copy-head phase transition: anchor for the trained tiny pointer-copy escalation.

Most important rev0032 result: symbolic copy-phase was escalated into a real trained tiny probe. Sparsemax and softmax both solved the small pointer-copy task; sparsemax reached the target faster in the smoke run, while relu/cosine variants lagged. This is not a proof of the phase-transition paper, but it gives the cube a concrete learned mechanism to harden.
