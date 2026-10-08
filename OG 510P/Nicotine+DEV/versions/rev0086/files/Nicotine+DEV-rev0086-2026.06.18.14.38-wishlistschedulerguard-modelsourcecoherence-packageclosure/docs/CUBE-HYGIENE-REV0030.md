# Cube hygiene — rev0030

## Compact-cube invariant

The large upstream source bundle remains external. Rev0030 records hashes, source-line traces, evidence logs, and maintainer artifacts, but does not embed `source-trees/github-*` directories.

## Generated cache pruning

During witness execution, pytest/Python generated cache directories under:

```text
maintainer_artifacts/wma-asf-tinystep-01/.pytest_cache
maintainer_artifacts/wma-asf-tinystep-01/__pycache__
```

These generated directories were pruned before packaging. The reproducible evidence is retained through the test file, source trace, run log, and probe helper.

## Refactor/audit pass

Rev0030 added a coherence split for local media-parser rows:

```text
U-273 WMA/ASF object progress: completed as WMA-ASF-TINYSTEP-01.
U-124 Ogg continuation accumulation: next target, kept separate.
U-125 MP4/M4A atom memory: separate memory-budget row.
U-127 FLAC STREAMINFO block: separate fixed-length validation row.
U-138 ID3v2 frame size: separate lower-value/public-ambiguous row.
U-248 share-scan cache: separate cache-provenance packet.
U-199 file-attribute count: separate network result/list parser packet.
```

## Audit artifacts

The final packaging pass generates:

```text
manifests/rev0030-file-manifest.json
manifests/rev0030-all-file-sha256.txt
manifests/rev0030-cube-audit.txt
```
