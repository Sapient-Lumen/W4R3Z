# Audited backlog addendum — rev0044

## New row action

```text
row: U-138 / general ID3v2 advertised-frame materialization
rev0044 action: boundary-demoted / archived
strict promotion: no
production-gated maintainer packet: no
```

## Evidence added

```text
maintainer_artifacts/u138-id3v2-frame-materialization-01/test_id3v2_frame_materialization_boundary_reproducer.py
tools/probe_rev0044_u138_id3v2_boundary.py
evidence/rev0044-u138-id3v2-boundary-rerun-matrix.txt
evidence/rev0044-u138-id3v2-boundary-source-trace.md
evidence/rev0044-web-public-overlap-u138-id3v2.md
data/rev0044_u138_id3v2_boundary_probe_summary.csv
```

## Short rationale

The row was originally useful as a media-parser audit prompt, but its broad form would overstate the Nicotine+ share-scanner MP3 path. The source trace shows share scanning calls TinyTag with `tags=False, duration=True`; the probe confirms that this path does not read a mapped ID3v2 text-frame payload as one advertised allocation on the archived source lanes.

The generic `tags=True` parser behavior remains documented for possible upstream TinyTag hardening review, but it is not elevated to strict/front status in this cube revision.

## Remaining strict/front inventory

```text
production-gated packets: 7
  - U-123
  - PB-01
  - SEARCH-RESP-01A
  - SEARCH-RESP-01B-BUDDY
  - SEARCH-RESP-PARSE-BUDGET-A
  - SEARCH-RESP-PARSE-BUDGET-B
  - SEARCH-RESP-01C-ROOM
production-ready disclosure texts in cube: 7
held search-response split rows: 0
held/deferred U-138 share-scanner row: 0 after rev0044 demotion
```
