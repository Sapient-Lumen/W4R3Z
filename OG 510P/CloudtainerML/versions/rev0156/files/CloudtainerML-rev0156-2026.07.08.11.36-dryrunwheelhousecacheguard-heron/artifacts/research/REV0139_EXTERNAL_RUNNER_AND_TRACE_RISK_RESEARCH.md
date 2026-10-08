# REV0139 external-runner and trace-risk research

This note records why rev0139 prioritizes a runnable packet over additional doctrine.

## Online grounding

- TinyLlama's model card describes the model as a compact 1.1B model using the same architecture and tokenizer family as Llama 2, supporting the Llama-specific trace surface while not itself proving CloudtainerML performance. Observed in web run: `turn287001view0` lines 187-190.
- Hugging Face Hub download docs say specific commit downloads should use full-length commit hashes and `snapshot_download()` can download a repository at a given revision. Observed: `turn356359view0` lines 117-125.
- The same docs describe `allow_patterns`, `ignore_patterns`, `local_dir`, and dry-run workflows. Observed: `turn356359view0` lines 143-170 and `turn356359view2` lines 202-229. This supports a small external runner that materializes reviewed files instead of carrying the full cube.
- Transformers attention-backend docs say `attn_implementation` selects the attention function and warn that custom attention implementations need matching mask handling. Observed: `turn287001view2` lines 126-160 and 212-217. This supports eager as trace semantics and SDPA/Flash as separate timing baselines.
- SLSA verification guidance says provenance matters only when consumers inspect it against expectations, including artifact/provenance matching and external parameter checks. Observed: `turn287001view4` lines 52-59 and 112-129.
- A 2026 artifact-evaluation paper frames reproduction as generating executable scripts and reports 44/60 reproduction scripts plus 20 newly uncovered errors. Observed: `turn399817view0` lines 22-26. Speculative relevance: executable runner packets are more likely to expose real defects than additional static registries.

## Applied conclusion

Rev0139 should not promote. It should reduce active-surface mass and make the next attempt binary: the external runner either produces a real trace/receipt chain or yields a specific runtime/snapshot failure from a compact surface.
