# rev0005 worklog — public-overlap machine and batch 01

Date: 2026-06-12 14:51 EDT

## Scope

This revision adds the repeatable public-overlap/audit machine requested by the user and starts applying it to the highest-ranked queue items. It does not embed the large upstream source bundle.

## Key decision

The cube must not present `fresh-unmentioned` as a final fact until hard searching is attached to that specific finding. The seed label is treated as a hypothesis.

## Batch touched

Batch 01 covers the leading FileTransferInit, FileSearchResponse, FolderContentsResponse, and PlaceInQueueRequest clusters.

Touched IDs:

```text
U-169, U-262, U-267, U-270, U-163, U-176, U-167, U-168, U-217, U-171, U-181, U-123, U-265, U-266, U-274, U-254, U-256
```

## Outcome

- Strict/high-quality document admissions remain: `0`.
- Public-overlap ledger now exists for all 274 seed rows.
- 17 high-ranked rows have initial or partial public-overlap classification.
- Several top rows are now marked public-adjacent or upstream-in-flight rather than clean fresh candidates.
- Current/future source snippets are recorded without embedding full source trees.

## Important downgrades / caution labels

- U-169 is not a clean fresh item because 3.3.11 RC release notes and future source lanes overlap the spoofed-user/unknown-token transfer-init family.
- U-274 is not a clean fresh item because public discussion/issue context already names repeated PlaceInQueueRequest/QueueUpload behavior and PR #3741 overlaps virtual path validation.
- U-256 is not a clean fresh item until PR #3741 scope is checked against request-side echo, not just response/list validation.
- U-266 is public-adjacent because public search-result hardlock/max_displayed_results context exists.

## Files added

```text
docs/PUBLIC-OVERLAP-POLICY.md
workspace/FINAL-DOC-CONSTRUCTION-MACHINE.md
workspace/WORKSPACE-ORGANIZATION-REV0005.md
data/rev0005_public_overlap_status.csv/json/jsonl
data/rev0005_hard_search_batch01.csv/jsonl
data/rev0005_ranked_audit_queue.csv/json
evidence/rev0005-web-public-overlap-batch01.md
evidence/rev0005-source-shape-batch01.md
tools/hard_search_workpacket.py
tools/source_probe_batch.py
```
