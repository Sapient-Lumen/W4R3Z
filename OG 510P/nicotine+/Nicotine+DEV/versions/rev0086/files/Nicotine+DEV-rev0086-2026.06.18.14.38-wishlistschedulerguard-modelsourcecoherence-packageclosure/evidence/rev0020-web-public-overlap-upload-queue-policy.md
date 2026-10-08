# rev0020 public-overlap notes — UPLOAD-QUEUE-POLICY-01 / U-244

Classification: **candidate no direct exact public match found / public-adjacent upload-queue-limit material exists**.

Targeted public searches performed:

```text
site:github.com/nicotine-plus/nicotine-plus upload queue megabyte limit queuelimit filelimit
site:github.com/nicotine-plus/nicotine-plus "Too many megabytes"
site:github.com/nicotine-plus/nicotine-plus "queuelimit" "upload"
site:github.com/nicotine-plus/nicotine-plus/issues "queue limit" "upload" "megabytes"
site:github.com/nicotine-plus/nicotine-plus/pull "queuelimit"
site:github.com/nicotine-plus/nicotine-plus/pull "Too many megabytes"
```

Relevant overlap found:

```text
- Official protocol documentation lists "Too many megabytes" as an in-use transfer rejection reason.
- Official protocol documentation defines QueueUpload and UploadDenied, which are the peer-message paths used by this reproducer.
- Official release notes mention a per-user upload queue limit specified in megabytes since old Nicotine lineage.
- GitHub issue #1985 is large-upload/"Too many megabytes"/queue-limiter adjacent but does not describe the candidate-size admission invariant.
```

No direct public issue/PR/advisory match was found for this exact invariant:

```text
QueueUpload or legacy TransferRequest admission checks only pre-existing queued megabytes,
then accepts a candidate file that alone exceeds the configured per-user megabyte limit
or causes existing_bytes + candidate_size to exceed the limit.
```

Decision: keep U-244 as verified audited-backlog hardening, not strict/front-lane.
