# REV0143 offline capture quarantine research

Purpose: ground the rev0143 change in current public documentation before changing the capture path. The working risk is that a nominally local evidence capture can still make Hub metadata calls, use an ambient implicit token, or resolve a different object unless the Hugging Face/Transformers offline boundary is set before runtime import and paired with `local_files_only=True`.

## Sources checked

- Hugging Face Hub environment-variable reference, retrieved 2026-07-08. It documents cache variables, token variables, Hub timeout variables, and the Hub offline/telemetry/implicit-token controls. Relevant retrieved lines: environment/cache/token defaults at L95-L124; timeout behavior at L132-L137; offline/disable controls were reviewed from the same official reference page.
- Transformers installation/offline-mode documentation, retrieved 2026-07-08. Lines L210-L233 state that offline/firewalled use requires downloaded and cached files ahead of time; `snapshot_download` is the documented preparation step; `HF_HUB_OFFLINE=1` prevents HTTP calls when loading; `local_files_only=True` is the documented cached/local-only loading path.
- Transformers `from_pretrained` model documentation, retrieved 2026-07-08. Lines L325-L336 tie `from_pretrained` to offline mode and local-directory loading.
- Hugging Face Hub file-download reference, retrieved 2026-07-08. Lines L189-L234 document `snapshot_download`, its `revision`, `token`, and `local_files_only` parameters, and `IncompleteSnapshotError` when the requested cached snapshot is incomplete while offline/local-only.

## Takeaways for this cube

1. Snapshot download/materialization and evidence capture should remain separate phases. Network can be permitted only in preparation; capture should be local-only.
2. Evidence capture needs two layers, not one: `local_files_only=True` inside `from_pretrained`/tokenizer/model calls, plus process environment controls before `huggingface_hub` or `transformers` are imported.
3. `HF_HUB_DISABLE_IMPLICIT_TOKEN=1` matters even for a public model because the default Hub client can use a local token on requests unless explicitly disabled. A public trace should not depend on or leak identity through an ambient account token.
4. `HF_HUB_DISABLE_TELEMETRY=1` and `HF_HUB_DISABLE_UPDATE_CHECK=1` are not scientific correctness requirements by themselves, but they help preserve a clean evidence-capture boundary: no optional phone-home behavior during receipt creation.
5. The strict expected failure in this chat/cloudtainer remains: no digest-verified local TinyLlama snapshot and no installed `transformers`. That is a healthy blocker, not a reason to loosen capture.

## Implemented rev0143 contract

`hf_transformers_offline_env_before_runtime_import_v1`

Capture path must set:

```bash
export HF_HUB_OFFLINE=1
export TRANSFORMERS_OFFLINE=1
export HF_HUB_DISABLE_TELEMETRY=1
export HF_HUB_DISABLE_IMPLICIT_TOKEN=1
export HF_HUB_DISABLE_UPDATE_CHECK=1
```

before importing the runtime. The capture helper records this in both the `.npz` payload and provenance JSON so a later selector/evaluator can reject traces that were captured under the wrong network boundary.
