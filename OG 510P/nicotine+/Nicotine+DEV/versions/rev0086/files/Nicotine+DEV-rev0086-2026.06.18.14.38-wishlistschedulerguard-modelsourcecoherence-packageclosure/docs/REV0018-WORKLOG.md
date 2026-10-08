# rev0018 worklog

## Completed

- Built and packaged `TRANSFER-SIZE-PROVENANCE-01` maintainer-style current-behavior tests.
- Ran the tests against all three archived source lanes.
- Confirmed U-69, U-107, and a combined U-198+U-107 consequence.
- Refreshed public-overlap classification for transfer-size, FileOffset/upload completion, shared-file/symlink/path behavior, and file-not-shared symptoms.
- Refactored the cluster so the cube does not over-present local/sync-race hardening as a strict peer-only issue.

## Run summary

```text
github-tag-3.3.10:   3 passed
github-branch-3.3.x: 3 passed
github-branch-master: 3 passed
```

## Strict lane

```text
strict report-candidates retained: 3
new strict promotions in rev0018: 0
production-ready disclosure texts: 0
```

## Files added

```text
maintainer_artifacts/transfer-size-provenance-01/test_transfer_size_and_file_provenance_reproducer.py
maintainer_artifacts/transfer-size-provenance-01/README.md
report_drafts/TRANSFER-SIZE-PROVENANCE-01-maintainer-hardening-skeleton.md

evidence/rev0018-transfer-size-provenance-pytest-run.txt
evidence/rev0018-transfer-size-provenance-source-trace.md
evidence/rev0018-web-public-overlap-transfer-size.md

data/rev0018_transfer_size_provenance_probe_summary.csv/json/jsonl
data/rev0018_public_overlap_transfer_size.csv/json/jsonl
data/rev0018_transfer_size_coherence_refactor.csv/json/jsonl
data/rev0018_queue_delta.csv/json/jsonl
data/rev0018_ranked_audit_queue.csv/json/jsonl
data/rev0018_strict_promotions.csv/json/jsonl
```
