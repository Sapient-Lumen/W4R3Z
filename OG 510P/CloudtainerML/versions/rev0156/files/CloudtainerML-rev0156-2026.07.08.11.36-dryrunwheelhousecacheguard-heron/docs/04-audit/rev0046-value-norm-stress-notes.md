# rev0046 value-norm stress notes

## Why this revision exists

rev0045 made score-only mass selection honest, but it still left a risky implicit assumption: preserving 0.95 attention probability mass is treated as if it preserves the softmax/V output. That is only safe when value vectors are bounded or when omitted value-norm tail risk is small.

rev0046 turns that assumption into an executable stress case.

## New falsifier

`experiments/value_norm_guarded_attention/value_norm_guarded_attention.py` generates QK/softmax/V rows across bounded, broad, and adversarial value-tail regimes. It compares:

- dense attention;
- exact Top-K;
- ordered Top-p;
- score-only histogram mass selection;
- histogram selection widened by scalar value-norm metadata;
- histogram selection plus discontiguous high `p_i ||V_i||` exceptions.

The metadata-guarded selectors may read scalar value norms but not value vectors or dense outputs. This deliberately changes the compiler contract and counts metadata reads separately from value reads.

## Scientific interpretation

The important result is not simply whether the new selector wins. The important result is the demotion:

> A score-only 0.95 mass certificate is not an output-quality certificate under value-tail risk.

If high-norm value vectors live in low-probability omitted tokens, mass-only selectors can satisfy the mass certificate and still fail output cosine or relative L2. A value-norm sidecar can repair many of those rows, but that creates a new systems obligation: norm metadata must be computed, stored, read, and scheduled cheaply enough to matter.

## Timing scope

`experiments/attention_selector_cpu_microbench` adds a native C++ selector-only CPU benchmark. It is useful because it replaces vague Python timing pressure with a measured native selector path. It is not an attention kernel, GPU kernel, or end-to-end model speed claim.

## Next repair

The next substantive step is a measured attention path: score scan, histogram, norm sidecar, exceptions, value gather, sparse softmax/output, and dense baseline on the same rows.
