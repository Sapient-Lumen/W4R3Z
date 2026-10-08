# rev0070 — two-stage certified support reuse

rev0069 showed that raw support reuse can be fast but invalid, while a full token-scan certificate is safe but slow.

This experiment tests a narrower repair: try a cheap scalar sidecar certificate first, then a block-summary certificate, and fall back to fresh full-row histogram selection only when the reusable anchor support cannot be bounded. The path remains local CPU evidence only and is not a sparse-attention promotion.
