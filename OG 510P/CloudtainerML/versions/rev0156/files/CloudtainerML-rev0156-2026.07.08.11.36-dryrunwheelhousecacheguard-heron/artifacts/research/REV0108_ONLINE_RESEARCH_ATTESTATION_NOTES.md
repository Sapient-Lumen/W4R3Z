# Online research notes — REV0108

Purpose: support the rev0108 move from path-bound receipts to content-addressed evidence receipts.

- SLSA provenance frames provenance as an attestation about produced artifacts and build definitions: https://slsa.dev/spec/v1.0/provenance
- SLSA's overall framework is about artifact integrity and tamper resistance: https://slsa.dev/
- in-toto statements bind predicates to subject artifacts: https://github.com/in-toto/attestation/blob/main/spec/README.md
- in-toto link ResourceDescriptors include names and digests: https://github.com/in-toto/attestation/blob/main/spec/predicates/link.md
- PyTorch warns reproducibility can vary by release/platform/device: https://docs.pytorch.org/docs/stable/notes/randomness.html
- Transformers exposes multiple KV cache strategies: https://huggingface.co/docs/transformers/en/kv_cache
- Transformers generation config includes generation/cache parameters: https://huggingface.co/docs/transformers/main_classes/text_generation
