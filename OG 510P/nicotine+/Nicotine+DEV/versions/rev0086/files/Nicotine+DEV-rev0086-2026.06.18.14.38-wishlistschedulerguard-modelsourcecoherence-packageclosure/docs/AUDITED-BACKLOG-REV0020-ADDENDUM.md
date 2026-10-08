# Audited backlog addendum — rev0020

rev0020 completed **UPLOAD-QUEUE-POLICY-01 / U-244** and kept it in the audited backlog rather than the strict/front lane.

## Verified in rev0020

```text
U-244 — Upload queue megabyte limit checks only pre-existing queued size, not candidate file size.
```

Current-behavior witness:

```text
maintainer_artifacts/upload-queue-policy-01/test_upload_queue_megabyte_limit_reproducer.py
```

Observed across all archived source lanes:

```text
github-tag-3.3.10:   6 passed
github-branch-3.3.x: 6 passed
github-branch-master: 6 passed
```

## Backlog classification

```text
status: verified audited-backlog hardening
strict document: not promoted
public overlap: candidate no direct exact public match found / public-adjacent queue-limit material exists
primary boundary: allowed requester can exceed intended per-user queued-megabyte cap at admission
impact: upload fairness, queue policy, bandwidth/availability hardening
```

## Queue refactor

```text
U-244 = canonical UPLOAD-QUEUE-POLICY-01 row.
U-271/U-274/U-47 = transfer-control string/request-budget lane; not merged.
U-166 = queue-position response provenance; not merged.
U-69/U-107/U-198/U-251 = transfer-size/provenance/send-lifecycle lanes; not merged.
```

## Next target

```text
U-248 — Share rescan cache reuses old file metadata when only mtime matches, without size or inode validation.
```

Why next: it may explain stale advertised size metadata feeding already verified upload-provenance/read/EOF families, but it needs a separate source/probe pass before we decide whether it is a real root or merely a support case.
