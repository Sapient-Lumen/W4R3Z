# rev0021 SHARE-SCAN-CACHE-01 probe summary

The maintainer-style pytest witness was run against all three archived source lanes.

```text
===== github-tag-3.3.10 =====
.....                                                                    [100%]
5 passed in 0.20s

===== github-branch-3.3.x =====
.....                                                                    [100%]
5 passed in 0.15s

===== github-branch-master =====
.....                                                                    [100%]
5 passed in 0.22s

```

Key finding: path + matching `st_mtime` is sufficient for the scanner to reuse old share metadata. The current file size is only read when the cache is bypassed or a rebuild is forced.
