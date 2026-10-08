# REV0142 research note — digest cache and Hugging Face snapshot path

Status: non-promotional. This note just records why REV0142 changes the runner surface.

## Online grounding

- Hugging Face Hub environment docs currently list `HF_HUB_DOWNLOAD_TIMEOUT` and `HF_HUB_ETAG_TIMEOUT`; the same page describes `HF_HUB_OFFLINE` for skipping HTTP calls when cached files are already available. Source: https://huggingface.co/docs/huggingface_hub/package_reference/environment_variables (observed via web.run: turn948532view0 lines 132-148 and 167-172).
- Transformers installation/offline docs say offline use requires files downloaded/cached ahead of time and shows `local_files_only=True` loading from a local directory. Source: https://huggingface.co/docs/transformers/installation (observed via web.run: turn948532view2 lines 210-233).
- Hugging Face Hub download docs describe `snapshot_download` for downloading/caching repository files. Source: https://huggingface.co/docs/huggingface_hub/en/guides/download (observed via web.run: turn948532view1 lines 79-85 and earlier REV notes).
- The TinyLlama `model.safetensors` page for a pinned file view lists a 2.2GB Xet-backed file and SHA-256 `6e6001da2106d4757498752a021df6c2bdc332c650aae4bae6b0c004dcf14933`. Source: https://huggingface.co/TinyLlama/TinyLlama-1.1B-Chat-v1.0/blob/2fef61190c752e2412f7b5dd2c2bde6f08fdb634/model.safetensors (observed via web.run: turn948532view4 lines 200-215).

## Speculation / risk call

The cube has been correctly insisting on a full `model.safetensors` digest before capture, but the live path can call multiple gates that all ask for `include_hashes=True`. On a 2.2GB file that is not a science signal; it is runner friction. The safe-ish repair is not to skip the digest, but to make the first full digest write a stat-bound receipt and let later same-file gates reuse it only while resolved path, size, mtime, ctime, device, and inode match. If the local filesystem itself is adversarial, operators can set `PUBLIC_TRACE_DISABLE_DIGEST_RECEIPT_CACHE=1` for a full rehash every time.

REV0142 also raises default Hugging Face Hub timeout values during snapshot materialization. The defaults can be too aggressive for a 2.2GB Xet-backed file on ordinary links; these defaults are operator-overridable and do not open the capture phase to network.
