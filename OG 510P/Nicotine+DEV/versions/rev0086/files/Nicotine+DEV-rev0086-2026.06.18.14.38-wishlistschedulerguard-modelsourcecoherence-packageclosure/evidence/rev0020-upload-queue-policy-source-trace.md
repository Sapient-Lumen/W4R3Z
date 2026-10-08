# rev0020 source trace — UPLOAD-QUEUE-POLICY-01 / U-244

Archived source lanes used from external rev0003 source bundle; the source trees are not embedded in this cube.

## Source file hashes

```text
4974bb9c71c173edc0bd529be34ccaa2c336abdbec573395f785375190eb355e  github-tag-3.3.10/pynicotine/uploads.py
78e864766dd96a33a790b571eb44a8f052c9ee1064fcb99f98c798900ba29db7  github-tag-3.3.10/pynicotine/transfers.py
b257035749e2779b3056344d727e51006ed5cb1ab566044992a2673020ae3bd3  github-branch-3.3.x/pynicotine/uploads.py
61e3c42c9f761d171c716892cd4832ef98fd6fd05cb45d553c0d7c3f132a4e55  github-branch-3.3.x/pynicotine/transfers.py
85fe39dc876097cade2a04dd40087a8a6af04ab30bf89fd551da12806226ee3a  github-branch-master/pynicotine/uploads.py
e8f04ede0635635f4eaf3445afa5ae417677af3489f3c306f9d1e43bc7e0a2cd  github-branch-master/pynicotine/transfers.py
```

## Core finding: queue megabyte limit checks only existing queued bytes

All three lanes implement `Uploads.is_queue_limit_reached(username)` using only existing `queued_users` count and existing `_user_queue_sizes[username]`.

```text
github-tag-3.3.10 uploads.py:221-232
  file_limit = config.sections["transfers"]["filelimit"]
  queue_size_limit = config.sections["transfers"]["queuelimit"] * 1024 * 1024
  if len(self.queued_users.get(username, {})) >= file_limit >= 1: reject Too many files
  if self._user_queue_sizes.get(username, 0) >= queue_size_limit >= 1: reject Too many megabytes

github-branch-3.3.x uploads.py:222-233
  same existing-state-only shape

github-branch-master uploads.py:220-231
  same existing-state-only shape
```

The candidate file size is not passed into `is_queue_limit_reached()`, so this helper cannot evaluate `existing_bytes + candidate_size > queue_size_limit`.

## Modern QueueUpload path

In `QueueUpload`, all three lanes check the queue limit before the candidate file size is obtained from shares.

```text
github-tag-3.3.10 uploads.py:468-475
  limit_reached, reason = self.is_queue_limit_reached(username)
  if limit_reached: return False, reason, size
  is_file_shared, size = core.shares.file_is_shared(username, virtual_path, real_path)

github-branch-3.3.x uploads.py:469-475
  same ordering

github-branch-master uploads.py:469-476
  limit_reached, reason = self.is_queue_limit_reached(username)
  if limit_reached: return False, reason, real_path, size
  real_path = core.shares.virtual2real(virtual_path)
  is_file_shared, size = core.shares.file_is_shared(username, virtual_path, real_path)
```

Then the `QueueUpload` handler constructs or updates a `Transfer` with the candidate size and enqueues it:

```text
github-tag-3.3.10 uploads.py:885-907
  transfer = Transfer(username, virtual_path, folder_path, size)
  self._append_transfer(transfer)
  self._enqueue_transfer(transfer)

github-branch-3.3.x uploads.py:877-900
  same shape with transferred_bytes_total reset for finished rows

github-branch-master uploads.py:956-982
  same shape plus lowercase/backslash compatibility flags and queued-upload notification option
```

`Transfers._enqueue_transfer()` then adds the candidate size into `_user_queue_sizes[username]` after admission:

```text
github-tag-3.3.10 transfers.py:487-496
  self.queued_users[transfer.username][transfer.virtual_path] = transfer
  self.queued_transfers[transfer] = None
  self._user_queue_sizes[transfer.username] += transfer.size

github-branch-3.3.x transfers.py:490-498
  same shape

github-branch-master transfers.py:488-496
  same shape
```

## Legacy TransferRequest download-request path

The legacy path goes through the same `_check_queue_upload_allowed()` helper. The rev0020 witness forces the "same user already active" branch so the accepted candidate is queued rather than immediately activated, making the queue accounting directly observable.

Observed behavior is identical across all lanes:

```text
existing queue below limit + oversized candidate + same-user active upload
  -> TransferResponse(allowed=False, reason=Queued)
  -> candidate is added to queued_users
  -> _user_queue_sizes becomes greater than configured queuelimit

existing queue already at limit + 1-byte candidate
  -> TransferResponse(allowed=False, reason=Too many megabytes)
  -> candidate is not queued
```

## What the witness proves

The maintainer-style pytest witness in `maintainer_artifacts/upload-queue-policy-01/test_upload_queue_megabyte_limit_reproducer.py` passed across all lanes with six tests each:

```text
github-tag-3.3.10:   6 passed
github-branch-3.3.x: 6 passed
github-branch-master: 6 passed
```

The pass file is `evidence/rev0020-upload-queue-policy-pytest-run.txt`.

## Interpretation

U-244 is source-confirmed and dynamically witnessed as current behavior, but it should remain audited-backlog rather than strict/front-lane:

```text
- The impact is upload policy/fairness/bandwidth availability, not code execution or file disclosure.
- The requester must already be allowed to queue/download the shared file.
- Public queue-limit and large-upload context exists, including the protocol's Too many megabytes rejection reason and historical release-note mention of per-user upload queue limits.
- The coherent fix is small but needs compatibility care: preserve first-file admission semantics if maintainers intentionally define the cap as "reject only once current queue is at/over limit," or change to candidate-inclusive accounting if the UI/docs promise "max megabytes per user in queue." Either way, the invariant should be explicit and tested.
```
