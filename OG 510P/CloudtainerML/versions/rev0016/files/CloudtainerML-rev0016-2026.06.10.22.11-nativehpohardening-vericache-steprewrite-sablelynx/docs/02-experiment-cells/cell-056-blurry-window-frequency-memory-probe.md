# CELL-056 — Blurry Window Frequency Memory Probe

Priority: P0

Status: candidate-with-runnable-probe

Source IDs: SRC-0107

## Cheap first run

Smooth-plus-spike signal reconstruction under finite state.

## Baselines

- sliding window
- exponential recency
- Fourier low-pass
- Fourier plus exact recent

## Metrics

- old MSE
- recent MSE
- spike MAE
- smooth MSE
- state units

## Stop condition

If blurry memory wins only on smooth no-spike cases, demote to narrow submodule.
