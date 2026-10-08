# Public trace probability semantics audit — rev0086

**Status:** `pass_with_blockers`

- probability contract: `float32_softmax_no_dropout_v1`
- attention probability dtype: `float32`
- fixture rows: `8`
- good bundle max dense error: `0.0`

## Negative controls

- `missing_probability_contract` rejected: `True` — probability_contract must be 'float32_softmax_no_dropout_v1'
- `float64_probability_dtype` rejected: `True` — attention_probability_dtype must be 'float32'
- `dropout_enabled` rejected: `True` — attention_dropout_p must be zero for public eager replay

## Interpretation

The public trace gate now requires the Llama eager probability path itself: float32 softmax, eval mode, zero dropout, and explicit attestation in both NPZ metadata and the provenance manifest. This prevents a dense-parity-compatible bundle from silently substituting float64 replay or train-mode/dropout semantics for the runtime probability path.
