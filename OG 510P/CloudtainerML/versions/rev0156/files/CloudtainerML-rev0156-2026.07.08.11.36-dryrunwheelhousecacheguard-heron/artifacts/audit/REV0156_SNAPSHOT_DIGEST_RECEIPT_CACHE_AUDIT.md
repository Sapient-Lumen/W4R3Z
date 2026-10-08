# Snapshot digest receipt cache audit — REV0156

Status: `pass`  
Promotion allowed: `false`

Guards the high-risk 2.2GB model hash path: the first full SHA-256 remains mandatory, but subsequent gates may reuse only a stat-bound receipt when path, resolved path, size, mtime, ctime, device, and inode are unchanged.

## Contract

- `stat_bound_model_safetensors_sha256_receipt_v1`
- First observed file identity computes a full SHA-256.
- Later unchanged identities may reuse the receipt.
- File mutation invalidates the receipt because stat identity changes.
- Set `PUBLIC_TRACE_DISABLE_DIGEST_RECEIPT_CACHE=1` to force full rehash.

## Errors

- none

## Warnings

- none
