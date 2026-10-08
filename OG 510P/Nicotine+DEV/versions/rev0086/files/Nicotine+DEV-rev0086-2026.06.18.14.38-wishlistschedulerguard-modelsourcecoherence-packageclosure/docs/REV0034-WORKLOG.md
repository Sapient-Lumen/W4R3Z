# rev0034 worklog

## Focus

Continued from rev0033's queue: **U-139 / FLAC share scanner parses leading ID3v2 frames despite duration-only metadata request**.

## Work performed

```text
1. Reviewed rev0033 queue, START-HERE notes, and FLAC media-parser split.
2. Traced share-scanner duration-only TinyTag routing and FLAC leading-ID3v2
   handling across:
   - github-tag-3.3.10
   - github-branch-3.3.x
   - github-branch-master
3. Built a compact synthetic FLAC-with-leading-ID3v2 witness.
4. Ran the witness against all three archived source lanes.
5. Captured the critical lane split: stable/3.3.x apply mapped ID3 tags despite
   tags=False; master avoids that mapped-frame application/materialization but
   still traverses the ID3 envelope.
6. Performed public-overlap review and conservative known/upstream-adjacent
   classification.
7. Added maintainer artifact, source trace, behavior JSON, pytest evidence,
   helper rerun, queue delta, strict decision rows, report skeleton, and
   coherence refactor.
8. Audited the media-parser cluster and separated U-139 from U-127 and U-138.
9. Pruned generated caches and produced fresh manifests/audit before packaging.
```

## Test result

```text
github-tag-3.3.10:   4 passed
github-branch-3.3.x: 4 passed
github-branch-master: 4 passed
```

## Decision

```text
verified audited backlog;
known/upstream-adjacent;
master partially fixes the mapped-frame/application shape;
not strict-promoted;
not production-ready disclosure text.
```
