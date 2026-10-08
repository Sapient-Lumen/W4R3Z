# SHARE-SCAN-CACHE-01 coherence/refactor — rev0021

## Canonical family

```text
SHARE-SCAN-CACHE-01 / U-248
  Share rescan cache reuses old file metadata when path + mtime match.
```

## Relationship to adjacent transfer/file-provenance work

Do **not** merge U-248 into TRANSFER-SIZE-PROVENANCE-01. It is an upstream input to stale advertised metadata, not the upload send-loop or F-init path itself.

```text
U-248  scan-cache provenance / stale metadata input
U-198  path/opened-file authorization provenance
U-107  upload read not clamped to advertised remaining size
U-251  upload EOF-before-advertised-size lifecycle
U-69   peer transfer-start filesize can expand queued download
```

The fix chain should be layered:

```text
1. Scanner metadata cache key should include size and, where reliable, file identity.
2. Upload F-init should revalidate/opened-file provenance and advertised size.
3. Upload sender should clamp reads to remaining advertised bytes.
4. Upload sender should handle EOF-before-size and >= advertised completion explicitly.
```

A scanner-only fix will not solve U-107/U-198/U-251. A transfer-only fix will not solve stale share advertisements/search results caused by cache reuse. They are coherent but not duplicates.

## Public-overlap consequence

U-248 was originally in the fresh/unmentioned seed, but rev0021 hard-search found direct public overlap. It should be moved to a public-known/verified-hardening lane. The cube should not count it as an unmentioned new problem.

## Priority after rev0021

```text
verified: yes
strict candidate: no
future usefulness: regression test + shared file-provenance fix support
recommended queue status: completed audited-backlog packet; do not revisit unless fixing the transfer/file-provenance chain together
```
