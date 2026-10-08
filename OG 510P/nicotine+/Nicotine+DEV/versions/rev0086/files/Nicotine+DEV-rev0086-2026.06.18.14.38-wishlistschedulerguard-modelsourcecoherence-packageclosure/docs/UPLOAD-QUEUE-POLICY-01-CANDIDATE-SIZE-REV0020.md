# UPLOAD-QUEUE-POLICY-01 / U-244 — queue megabyte cap ignores candidate size — rev0020

Status: **verified audited-backlog hardening packet; not strict-promoted**.

Lead row:

```text
U-244 — Upload queue megabyte limit checks only pre-existing queued size, not candidate file size.
```

## What rev0020 proved

A maintainer-style current-behavior witness now exists at:

```text
maintainer_artifacts/upload-queue-policy-01/test_upload_queue_megabyte_limit_reproducer.py
```

It passed against all archived source lanes:

```text
github-tag-3.3.10:   6 passed
github-branch-3.3.x: 6 passed
github-branch-master: 6 passed
```

The witness proves six current behaviors.

### 1. A first candidate can exceed the configured megabyte limit

Probe shape:

```text
configured queuelimit: 1 MiB
existing queued bytes: 0
candidate file size:  2 MiB
observed result:      queued
observed queue bytes: 2 MiB
observed denial:      none
```

This is the minimal U-244 proof. The queue megabyte cap is not candidate-inclusive at admission time.

### 2. A candidate can push an existing queue over the limit

Probe shape:

```text
configured queuelimit: 1 MiB
existing queued bytes: 700 KiB
candidate file size:  500 KiB
observed result:      queued
observed queue bytes: 1200 KiB
observed denial:      none
```

This is the policy/fairness consequence. A requester can keep the queue below the cap before admission, then cross it with the candidate file.

### 3. Rejection works only after the existing queue is already at the limit

Probe shape:

```text
configured queuelimit: 1 MiB
existing queued bytes: 1 MiB
candidate file size:  1 byte
observed result:      rejected
observed reason:      Too many megabytes
```

This proves the queue limiter is present and functional, but its boundary is existing queue size rather than existing-plus-candidate size.

### 4. The file-count limit has different semantics

With `filelimit=1` and megabyte limit disabled, the first file is accepted and the second is rejected as `Too many files`.

That means rev0020 should not describe U-244 as “all queue limits ignore candidates.” The count limit already behaves as a maximum number of existing queued items, while the megabyte limit ambiguity is about whether a candidate file should be included in the total byte cap.

### 5. Legacy `TransferRequest` shares the root

The legacy download-request path uses the same queue-admission helper. When the same user already has an active upload, a legacy candidate larger than the configured megabyte limit is queued and returns:

```text
TransferResponse(allowed=False, reason=Queued)
```

This matters because a coherent fix should cover both modern `QueueUpload` and legacy `TransferRequest` download-request compatibility paths.

### 6. Legacy rejection still works once the existing queue is already at the cap

The legacy path rejects with `Too many megabytes` when the existing queued bytes are already at the configured limit. Again, the root is not “no limit exists”; the root is “the limit does not include candidate file size at admission.”

## Source-shape summary

All three source lanes keep the same relevant structure:

```text
Uploads.is_queue_limit_reached(username)
  reads filelimit and queuelimit
  compares len(queued_users[username]) to filelimit
  compares _user_queue_sizes[username] to queuelimit bytes
  does not accept candidate_size

Uploads._check_queue_upload_allowed(...)
  calls is_queue_limit_reached(username)
  only after that calls file_is_shared(...), which returns candidate size

Transfers._enqueue_transfer(transfer)
  adds transfer.size into _user_queue_sizes[username] after admission
```

Full line references are in:

```text
evidence/rev0020-upload-queue-policy-source-trace.md
```

## Public-overlap assessment

Classification:

```text
candidate no direct exact public match found / public-adjacent upload-queue-limit material exists
```

Public material exists for Nicotine+ upload queue megabyte limits and the `Too many megabytes` rejection reason. GitHub issue #1985 is large-upload/queue-limiter adjacent. Targeted searches did not find a direct public report of the narrower invariant that `QueueUpload` or legacy `TransferRequest` admission checks only pre-existing queued megabytes and then queues a candidate that alone exceeds, or pushes the queue beyond, the configured megabyte cap.

See:

```text
evidence/rev0020-web-public-overlap-upload-queue-policy.md
```

## Why this is not strict-promoted

U-244 is real and verified, but it does not become the fourth strict report-candidate in rev0020 because:

```text
- impact is queue policy/fairness/bandwidth availability, not code execution or file disclosure;
- requester must already be permitted to queue/download the shared file;
- large upload and queue-limit behavior has public-adjacent history;
- the fix may be a product semantics decision rather than a clear security boundary;
- stronger strict candidates already exist for transfer-token, peer-primary-election, and search-response source/scope binding.
```

## Fix shape

A coherent fix has to decide semantics explicitly.

Candidate-inclusive cap:

```text
- look up candidate file size before megabyte queue-limit decision;
- reject if existing_queued_bytes + candidate_size > queue_size_limit;
- preserve `friendsnolimits`/buddy exemptions;
- apply to modern QueueUpload and legacy TransferRequest;
- send `UploadDenied(..., Too many megabytes)` or legacy TransferResponse reason consistently;
- add tests for first oversized candidate, aggregate-over-limit candidate, exactly-at-limit candidate, friends exemption, filelimit interaction, legacy path, and active-upload path.
```

If maintainers intentionally want current semantics:

```text
- document that queuelimit rejects only once existing queued bytes are already at/over cap;
- add regression tests preserving that behavior;
- consider renaming or UI clarification so users do not expect a hard maximum queued megabytes per user.
```

## Decision

```text
U-244: verified audited backlog; not strict-promoted.
U-271/U-274/U-47: separate transfer-control string/request-budget lane.
U-166: separate queue-position provenance/UI lane.
U-69/U-107/U-198/U-251: separate transfer-size/provenance/send-lifecycle lanes.
```
