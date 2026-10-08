# External source inventory — rev0004

The source payload is deliberately **not** included in this cube.

## External bundle

Archive: `Nicotine+DEV-rev0003-upstream-sources-20260612T181540Z.zip`  
SHA256: `feaa8df98bbd0f28ba00eb8d52dcc3b9b9860e8d59039c7d41a98a0117505e5b`  
Role: source-reference bundle for evaluation.

## Source lanes

| lane | commit | purpose |
|---|---|---|
| `github-tag-3.3.10` | `caf9e101a841ff2e0a96aebc8e07bbf7ff1b2026` | current stable tag/source baseline |
| `github-branch-3.3.x` | `98089ac233aa57786e8dbdc48123f6ac1c4767d8` | supported 3.3.x / release-candidate maintenance lane |
| `github-branch-master` | `f4e17d59783dbc48ea31d2e899a681e2dd1ed500` | future/default development lane |


## What rev0004 carries instead of source blobs

- `sources/source_lanes_external_rev0003.csv` — lane commit IDs, counts, tree hashes.
- `sources/source_code_file_hashes_rev0003.csv` — compact code/UI/document file hash index.
- `sources/source_code_delta_matrix_rev0003.csv` — paths whose code/UI/document hash differs between source lanes.
- `sources/metadata_snapshot_rev0003/` — GitHub metadata, fetch logs, and bundle SHA256SUMS.

## Local runtime note

In this assistant runtime, the source trees were extracted for future analysis under:

`/mnt/data/nicotine_dev_external_source_inventory/Nicotine+DEV-rev0003-upstream-sources-20260612T181540Z/source-trees/`

That path is not meant as portable archive content. Use the external rev0003 source bundle if you need to reconstruct the same source inventory elsewhere.
