# REV0127 baseline and snapshot-risk research notes

Status: `non_promotional_research_note`

## Snapshot path

The immediate execution risk was local, not theoretical: a local minimum-size threshold exceeded the published size of the locked file. Hugging Face's Hub docs describe `snapshot_download()` as downloading a repository at a selected revision and caching it locally, with file filtering (`allow_patterns`) and dry-run planning. The pinned TinyLlama tree and config page show that `config.json` is 608 bytes, so a `>=1000` threshold was impossible for the legitimate locked file.

## Performance pressure

Even after trace capture works, sparse-attention promotion remains hard. PyTorch's `scaled_dot_product_attention` is the dense semantic baseline; FlashAttention-style exact kernels reduce IO and memory overhead; modern serving systems also make KV-cache layout and paging central. CloudtainerML should therefore keep sparse claims bracketed against the installed exact/eager/SDPA/Flash/Flex/page-KV or local equivalents before any speed statement.

## Operational consequence

Rev0127 makes the snapshot preflight less wasteful: it should no longer reject the valid TinyLlama config before the operator can discover the next true blocker. This is forward motion because it removes one false negative from the highest-risk path: digest-authenticated public snapshot → local-only trace capture → receipts → named-hardware timing.
