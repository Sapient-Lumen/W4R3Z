# Downstream receipt-chain research — REV0136

Status: `research_note_non_promotional`  
Promotion allowed: `false`

Rev0136 applies a narrower online lesson: local/offline model execution and portable handoff are only reviewable when every downstream receipt remains bound to digest-named subjects, not to mutable cache resolution or path labels. Hugging Face documents `from_pretrained("./path/to/local/directory", local_files_only=True)` for local/offline loading, and `snapshot_download()` materializes a repository snapshot at a revision into local files. Safetensors is a safe/fast tensor container, and its metadata can be cheaply parsed, but header/metadata checks are not the same thing as authenticating the full weight bytes; the cube therefore continues to require the pinned `model.safetensors` SHA-256. The practical receipt-chain lesson from SLSA and in-toto style attestations is that a downstream decision should bind subjects by digest plus predicate/contract fields.

## Applied change

- Added `public_trace_selector_entry_chain_v1` as a non-circular selector-entry chain digest.
- The selector-entry receipt now binds the accepted evaluation receipt SHA-256, evaluation subject-set SHA-256, downstream `trace_identity_sha256`, actual replay bundle subject-set SHA-256, and selector gate tool SHA-256.
- The replay gate recomputes the chain from actual files/tools instead of trusting receipt path labels.
- The handoff builder and handoff gate now carry and replay `selector_entry_chain_sha256`, so a copied selector receipt cannot be paired with a different evaluation/trace/provenance/tool bundle.
- Current run wrappers were refactored to remove duplicate acceptance-loader-binding audit calls and to use the actual preflight CLI shape: `--phase capture --strict` rather than the broken `--strict capture` argument order.

## Sources consulted

- https://huggingface.co/docs/transformers/en/installation — Transformers supports local/offline loading from a local directory with `local_files_only=True` after files are downloaded.
- https://huggingface.co/docs/huggingface_hub/en/guides/download — `snapshot_download()` downloads a repository snapshot at a revision and stores files locally/cache-backed.
- https://huggingface.co/docs/huggingface_hub/en/package_reference/utilities — HF offline mode is an explicit environment state; capture receipts should not depend on implicit network/cache behavior.
- https://huggingface.co/docs/safetensors/en/index — safetensors is a safe, fast tensor storage format, but format safety is not full-byte provenance.
- https://huggingface.co/docs/safetensors/en/metadata_parsing — safetensors metadata/header parsing is cheap and useful for structure, while full digest checks still authenticate bytes.
- https://slsa.dev/spec/v1.0/provenance — provenance consumers verify named subjects and digests rather than informal path labels.
- https://github.com/in-toto/attestation/blob/main/spec/README.md — in-toto attestations bind subject digests to predicate facts; rev0136 mirrors that pattern for trace/evaluation/selector handoff receipts.
