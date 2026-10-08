# Trace packet speed envelope audit — rev0063

**Status: pass**

rev0063 measures an oracle/free-selector sparse speed envelope. It can show headroom, but cannot promote the mechanism because the Top-p support is supplied from full-score oracle information and all QK scores are still computed.

## Key metrics
- oracle Top-p 0.96 QK-included speedup vs dense: `1.17350057689`
- oracle Top-p 0.96 value-only speedup vs dense value-only: `0.69679373458`
- quality rate: `1`
- selected fraction: `0.4327392578125`

## Warnings
- oracle/free-selector qk-included path clears dense in this noisy CPU run; this is headroom, not a deployable selector result
- sparse value-only accumulation is slower than dense value-only here; branch/gather overhead remains material
