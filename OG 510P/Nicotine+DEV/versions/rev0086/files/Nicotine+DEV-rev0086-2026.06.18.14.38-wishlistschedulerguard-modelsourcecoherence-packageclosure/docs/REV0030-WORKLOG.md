# rev0030 worklog

## Target

Queued target from rev0029: **WMA/ASF parser tiny-step amplification / U-273**.

## Source trace

Checked all three archived lanes from the rev0003 source bundle:

```text
github-tag-3.3.10
github-branch-3.3.x
github-branch-master
```

All three route WMA metadata through TinyTag from the share scanner. All three reject `object_size == 0` and `object_size > filesize`, but do not reject `0 < object_size < 24` before the unknown-object relative seek.

## Dynamic proof

Added:

```text
maintainer_artifacts/wma-asf-tinystep-01/test_wma_asf_tinystep_reproducer.py
tools/probe_rev0030_wma_asf_tinystep.py
```

Captured:

```text
evidence/rev0030-wma-asf-tinystep-pytest-run.txt
```

Run summary:

```text
github-tag-3.3.10:   3 passed
github-branch-3.3.x: 3 passed
github-branch-master: 3 passed
```

## Public-overlap pass

Captured public-overlap notes in:

```text
evidence/rev0030-web-public-overlap-wma-asf-tinystep.md
manifests/web-references-rev0030.md
manifests/web-references-rev0030.json
```

Classification: candidate no-direct-public-found / public-source and ASF-parser-class adjacent.

## Refactor/audit

Added a media-parser coherence split so U-273 remains separate from U-124, U-125, U-127, U-138, U-248, U-199, and broad network caps. Updated strict/front-lane docs, ranked queue docs, and next-revision queue.
