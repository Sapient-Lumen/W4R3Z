# Downstream identity receipt research — REV0136

Status: `research_note_non_promotional`  
Promotion allowed: `false`

Rev0136 applies the online lesson that local/offline model execution is only reproducible when the exact downloaded snapshot path and digests survive downstream use. Hugging Face documents local/offline loading and snapshot materialization; SLSA/in-toto provenance models digest-bound subjects/materials. The practical cube change is to make evaluation, selector-entry, replay, and handoff archives carry a compact `trace_identity_sha256` rather than relying on a vague verifier-accepted boolean.

## Applied change

- Added `public_trace_downstream_identity_receipt_v1`.
- Evaluation receipts now summarize selected snapshot path, prompt manifest hash, generation/cache contract, and `model.safetensors` SHA-256.
- Selector-entry and replay gates cross-check that identity hash.
- Handoff manifests carry `trace_identity_chain_bound` and replay the selector/evaluation identity match.

## Sources consulted

- https://huggingface.co/docs/transformers/en/installation — Transformers supports offline/local loading from a local directory with local_files_only once files are downloaded.
- https://huggingface.co/docs/huggingface_hub/en/guides/download — snapshot_download materializes a repository snapshot and can pin a revision.
- https://huggingface.co/docs/huggingface_hub/en/package_reference/environment_variables — HF cache locations are configurable, so receipts should avoid relying on implicit cache resolution.
- https://slsa.dev/spec/v1.0/provenance — SLSA provenance models how an artifact was produced and supports consumer verification.
- https://github.com/in-toto/attestation/blob/main/spec/predicates/link.md — in-toto link descriptors require names and digests, matching the need for digest-bound downstream trace identity.
