# CELL-085 — State-Tracking Layer Reversal Bench

Priority: **P1**
Status: **candidate**

## Cheap first run

Train tiny sequence models on alternate state-tracking encodings and probe layerwise state.

## Sources

SRC-0141, SRC-0142

## Baselines

- Transformer
- linear RNN
- nonlinear RNN
- memory transformer

## Metrics

- state probe accuracy
- layer peak
- generalization length
- trace loss

## Stop condition

If layer probes are unstable, simplify automata.
