# Runtime research notes — rev0086

## Focus

The rev0086 change targets probability semantics for public Llama-family trace capture. The risk is a false public trace acceptance where Q/K/V score parity is correct but the probability path is underspecified or wrong.

## Online findings used

- Hugging Face Transformers current Llama eager attention expands compact K/V heads with `repeat_kv`, computes scaled QK scores, adds `attention_mask`, then calls `nn.functional.softmax(..., dtype=torch.float32).to(query.dtype)` before dropout and value matmul. This supports requiring a `float32_softmax_no_dropout_v1` public contract for eval captures.
- Hugging Face AttentionInterface documentation states that custom attention backends also need matching AttentionMaskInterface behavior; otherwise mask creation may be skipped and `attention_mask=None` can be passed. This supports keeping mask fidelity and probability semantics coupled.
- Hugging Face cache documentation distinguishes dynamic, static, sliding-window, and offloaded caches; static/sliding storage can include physical slots that are not active scored keys. This supports retaining the active-key and absolute-position gates alongside probability semantics.
- PyTorch SDPA exposes grouped-query attention controls, and current optimized attention backends continue to differ in dispatch/materialization details. This supports treating public trace acceptance as a runtime-path contract rather than a registry statement.

## Resulting design choice

Rev0086 does not promote performance or model evidence. It adds an admission rule: a public/pretrained attention trace must attest and gate-check float32 softmax/no-dropout probability semantics. Negative controls prove the gate rejects missing probability contract, float64 probability dtype, and dropout-enabled metadata while the same dense fixture remains mathematically reconstructible.
