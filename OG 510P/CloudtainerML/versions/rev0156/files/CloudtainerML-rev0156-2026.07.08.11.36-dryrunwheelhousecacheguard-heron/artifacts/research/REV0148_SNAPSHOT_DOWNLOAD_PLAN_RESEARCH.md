# REV0148 online research note — snapshot download-plan gate

The riskiest unfinished work is still one real public TinyLlama trace. The new completion risk addressed here is waste before evidence: a capable machine could spend network and disk on the large snapshot before proving the planned file set, commit, cache root, and local free-space budget are coherent.

Online grounding used this turn:

- Hugging Face Hub download docs describe dry-run mode and state that programmatic `snapshot_download(dry_run=True)` returns file info including commit hash, file name, size, cache status, and whether a file would be downloaded.
- Hugging Face Hub environment docs state that Hub environment variables are read at import time and define `HF_HOME`, `HF_HUB_CACHE`, and `HF_XET_CACHE`; the runner must bind project-local cache roots before importing Hub code.
- Hugging Face cache docs describe the cache root and snapshots-by-revision structure; this supports checking the planned cache target before materialization.
- Transformers attention-interface docs emphasize that attention backend and mask semantics are backend-sensitive; the capture still stays on `attn_implementation=eager` and treats alternative kernels only as later timing baselines.

Decision: add an executable dry-run/byte-budget gate in the snapshot-preparation phase. Do not loosen the offline evidence-capture quarantine.
