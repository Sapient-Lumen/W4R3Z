# Online research notes — REV0109

Status: `pass_with_blockers`  
Promotion allowed: `false`

The useful research signal for this turn is attestation discipline, not more doctrine. Hugging Face's attention-backend and cache-strategy documentation reinforces that backend/cache/runtime semantics are explicit evidence variables, while PyTorch CUDA event documentation reinforces that timing evidence must be bound to synchronized timing semantics. SLSA and in-toto attestation models reinforce the core refactor: selector entry should be a separate digest-bound handoff receipt over the evaluation receipt, actual files, and tool hashes.

## Sources used

- Hugging Face attention backends: https://huggingface.co/docs/transformers/en/attention_interface — attn_implementation is an explicit model-loading/runtime variable; trace receipts should not let backend identity drift.
- Hugging Face cache strategies: https://huggingface.co/docs/transformers/en/kv_cache — Transformers exposes dynamic/static/offloaded/quantized cache options; cache identity must stay bound in the trace evidence.
- PyTorch CUDA Event docs: https://docs.pytorch.org/docs/stable/generated/torch.cuda.Event.html — CUDA events are synchronization markers for timing; timing receipts must distinguish diagnostic capture timing from named-hardware promotion timing.
- SLSA provenance v1.0: https://slsa.dev/spec/v1.0/provenance — Provenance binds produced artifacts through subject digests; rev0109 applies this to selector-entry handoff.
- in-toto attestation statement spec: https://github.com/in-toto/attestation/blob/main/spec/README.md — Attestation statements bind predicates to subjects; selector-entry is now represented as a separate predicate over the evaluation receipt, files, and tools.
- in-toto link predicate / ResourceDescriptor: https://github.com/in-toto/attestation/blob/main/spec/predicates/link.md — Resource descriptors with names and digests informed the semantic subject-name + sha256 structure.
