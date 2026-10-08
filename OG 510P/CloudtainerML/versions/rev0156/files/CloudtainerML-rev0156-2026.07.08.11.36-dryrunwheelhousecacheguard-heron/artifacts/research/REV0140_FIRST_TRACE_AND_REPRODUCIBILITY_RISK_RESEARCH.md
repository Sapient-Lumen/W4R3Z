# REV0140 first-trace/reproducibility risk research

This note is not evidence for CloudtainerML performance. It records why REV0140 chose executable runner repair over another doctrine/registry pass.

## Sources checked online during this turn

1. Hugging Face Hub download guide — `https://huggingface.co/docs/huggingface_hub/en/guides/download`.
   - Relevant observed facts: full-length commit hashes are required for commit-specific downloads; `snapshot_download` supports repository snapshots at a revision; downloads can be filtered; local folders and dry-run planning are supported.
   - Cube implication: the first public trace path should explicitly separate reviewed snapshot materialization from local-only evidence capture.

2. Transformers attention backend documentation — `https://huggingface.co/docs/transformers/en/attention_interface`.
   - Relevant observed fact: 4D attention mask conventions differ by backend; eager uses additive float masks, while SDPA/Flash/Flex use different accepted forms.
   - Cube implication: `ATTENTION_IMPLEMENTATION=eager` remains the semantic trace lane; fused kernels are not trace substitutes.

3. Safetensors documentation — `https://huggingface.co/docs/safetensors/index`.
   - Relevant observed fact: safetensors is a safe and fast tensor storage format with partial tensor access.
   - Cube implication: safetensors format validity is helpful but insufficient; public evidence still requires explicit weight-file SHA-256 binding.

4. Artisan: Agentic Artifact Evaluation — `https://arxiv.org/abs/2602.10046`.
   - Relevant observed fact: the paper frames artifact reproduction as executable scripts that can be run independently and reports reproduction-script generation plus error discovery.
   - Cube implication: a one-command first-trace runner is more mission-aligned than another narrative audit.

5. Large Language Models for Software Engineering: A Reproducibility Crisis — `https://arxiv.org/abs/2512.00651`.
   - Relevant observed fact: the study reports persistent gaps in environment specification, versioning, model/access/legal details, and execution fidelity.
   - Cube implication: the runner must emit status receipts and preserve model/source/license boundaries.

## Speculative risk read

The biggest waste risk is now not a missing conceptual registry. It is a high-friction external execution surface: a future operator may install dependencies, download a snapshot, run the wrong wrapper, or fail without a status receipt. REV0140 therefore adds a one-command path and a surface audit that makes the expected failure small and actionable.
