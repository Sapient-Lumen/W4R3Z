# rev0064 value-layout envelope audit

rev0063 showed that the sparse value-only path was slower than dense value-only. rev0064 checks whether that was a mechanism failure or a layout/schedule artifact.

The new native replay separates mask scanning from selected-index and packed-value schedules. The exact Top-p support is still supplied from full dense scores, so no result here promotes a deployable selector.

## Findings

- Mask-scan sparse value-only is slower than dense value-only.
- Selected-index gather and sorted gather are faster than dense value-only on the local tiny-trained trace.
- Prepacked selected values are faster still.
- The oracle packed QK-included path clears dense on this CPU trace, but it still computes all QK scores and uses oracle support/layout side inputs.

## Interpretation

The important correction is that sparse value accumulation is not inherently dead on this trace; the bad rev0063 value-only number was partly a mask-scan layout artifact. The result is still non-promotional because exact Top-p support and packed values are not deployable selector evidence, public/pretrained traces are missing, and GPU/fused timing is missing.
