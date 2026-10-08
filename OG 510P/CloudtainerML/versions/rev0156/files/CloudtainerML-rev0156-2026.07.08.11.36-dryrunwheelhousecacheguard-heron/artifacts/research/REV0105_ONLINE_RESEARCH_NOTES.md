# Online research notes — REV0105

Purpose: support the acceptance-bundle gate with current public documentation, while keeping the next action operational rather than doctrinal.

## Sources checked

- Hugging Face Transformers KV cache docs: https://huggingface.co/docs/transformers/en/kv_cache
  - Relevance: generation can use different cache implementations, including dynamic, static, offloaded, and quantized/offloaded variants. A trace bundle must explicitly bind the dynamic-cache choice used for replay rather than inheriting defaults.
- Hugging Face Transformers model loading docs: https://huggingface.co/docs/transformers/en/main_classes/model
  - Relevance: model loading can infer or resolve dtype from checkpoints/config; a replayable trace should record requested dtype, resolved dtype, model parameter dtype set, and device placement.
- Hugging Face Accelerate big-model inference docs: https://huggingface.co/docs/accelerate/en/concept_guides/big_model_inference
  - Relevance: device placement can be automatic and split across resources. Public trace provenance must preserve actual device placement and keep local loader paths separate from canonical HF model identity.
- PyTorch CUDA Event docs: https://docs.pytorch.org/docs/stable/generated/torch.cuda.Event.html
  - Relevance: GPU timing needs explicit timing and synchronization semantics. Capture elapsed time remains diagnostic; promotion timing requires a separate named-hardware run.

## REV0105 interpretation

The riskiest remaining failure is no longer just “can we capture a trace?” It is “can a captured trace survive replay, gate validation, and later evaluation without missing metadata?” REV0105 therefore treats the artifact pair as an acceptance bundle: NPZ tensors, provenance JSON, embedded self-attestation, token/prompt replay fields, cache identity, runtime provenance, score semantics, and dense-reference parity must all agree.

## Practical consequence

After any successful capture, do not evaluate or promote from the NPZ alone. Validate the NPZ plus provenance JSON through the public gate path and preserve the exact report. If the report fails, repair only the failing executable seam.
