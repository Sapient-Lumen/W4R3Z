# Draft maintainer hardening note — UPLOAD-QUEUE-POLICY-01 / U-244

Status: **not production-ready disclosure text**.

## Summary

The upload queue megabyte limit currently checks only the number of bytes already queued for the requester. The candidate file size is looked up after the queue-limit check, so a requester who is otherwise allowed to download can queue a first file larger than the configured per-user megabyte queue cap, or queue a file that pushes their aggregate queued size over the cap.

## Affected paths

```text
modern QueueUpload
legacy TransferRequest with direction=DOWNLOAD when queued rather than immediately started
```

## Current-behavior witness

```text
maintainer_artifacts/upload-queue-policy-01/test_upload_queue_megabyte_limit_reproducer.py
```

Observed in archived lanes:

```text
github-tag-3.3.10:   6 passed
github-branch-3.3.x: 6 passed
github-branch-master: 6 passed
```

## Impact boundary

```text
- upload queue policy/fairness and bandwidth/availability hardening;
- requester must already be permitted to queue/download the shared file;
- not code execution;
- not direct file disclosure;
- not a peer-identity/source-binding issue by itself.
```

## Fix options

Candidate-inclusive cap:

```text
if queue_size_limit >= 1 and existing_queued_bytes + candidate_size > queue_size_limit:
    reject Too many megabytes
```

Compatibility-preserving current semantics:

```text
Document/test that queuelimit rejects only once existing queued bytes are already at or above the cap.
```

The first option should add tests for modern and legacy request paths, first oversized file, aggregate-over-limit file, exactly-at-limit file, file-count interaction, and buddy/friend exemptions.
