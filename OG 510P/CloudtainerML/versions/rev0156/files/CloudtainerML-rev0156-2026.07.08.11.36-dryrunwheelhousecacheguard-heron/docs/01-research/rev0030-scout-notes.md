# rev0030 scout notes

## Fresh performance-core additions

- Phase Transitions in Attention / copy-head emergence: gives a crisp tiny mechanistic screen with softmax first-order versus linear second-order/crossover behavior.
- LoLA: use sparse cache plus linear attention as an alternative to direct sparse attention.
- Confidence-Adaptive SwiGLU: useful only with rare-expert and overconfident-wrong guard fields.
- GBLA: local mixing + key gating + output gating belongs as a bidirectional long-history linear-attention P1 lane.

## Main steer

Rev0030 hardens spectral/operator routing but promotes copy-head phase transition as the strongest trained-tiny candidate.
