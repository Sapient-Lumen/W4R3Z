# Snapshot integrity / phase research — REV0121

Status: `research_applied`  
Promotion allowed: `false`

The external references support a narrow engineering correction: the Hub snapshot/materialization step and the Transformers model-load/capture step should not share the same blocker set. Offline Transformers use requires downloaded/cached files first; `snapshot_download` can obtain a revision-filtered file set; and safetensors headers can be parsed cheaply before loading tensor buffers.

## Applied change

- `--phase snapshot` defers capture-only missing packages such as `transformers`.
- `--phase capture` keeps those packages as hard blockers.
- Local snapshot readiness now rejects filename-only fake snapshots and pointer/partial/sparse weight files.

## Sources recorded

- Hugging Face Transformers installation/offline mode docs.
- Hugging Face Hub download and file-download docs.
- TinyLlama model.safetensors file page.
- Safetensors metadata parsing docs.
