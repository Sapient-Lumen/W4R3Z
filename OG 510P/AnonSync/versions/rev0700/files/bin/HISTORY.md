# Packaged binaries

The slim cube packages only the current active executable to avoid carrying stale runnable artifacts.

- rev0700: `bin/rev0700/anonsync_core-linux-x86_64-gcc-openssl3-sqlite3` — release build containing a bounded mutating scheduler executor over persisted resume-transfer workorder actions, `allowed_execution_idempotency_keys` filters for claim/execution mutators, complete returned scheduler group consumption, observation-only handling for non-mutating action classes, and `--selftest-sync-domain-model`.
- rev0699: historical source/audit only in this package; the rev0699 runnable binary is intentionally omitted. `bin/rev0699/anonsync_core-linux-x86_64-gcc-openssl3-sqlite3` — release build containing scheduler batch-boundary hardening over persisted resume-transfer workorder actions, complete `execution_idempotency_key` group planning, deferred group counters for too-small `max_scheduler_actions`, and `--selftest-sync-domain-model`.
- rev0698: historical source/audit only in this package; the rev0698 runnable binary is intentionally omitted. `bin/rev0698/anonsync_core-linux-x86_64-gcc-openssl3-sqlite3` — release build containing a bounded scheduler action planner over persisted resume-transfer workorder queue facts, action classes for execute-owned, claim-or-reclaim-expired, abandon-expired, wait-retry-backoff, live-other observation, terminal review, completed-row ignore, and `--selftest-sync-domain-model`.
- rev0697: historical source/audit only in this package; the rev0697 runnable binary is intentionally omitted. `bin/rev0697/anonsync_core-linux-x86_64-gcc-openssl3-sqlite3` — release build containing a read-only persisted resume-transfer workorder queue selector over owned live claims, live claims held by other workers, expired cooling-down rows, retry-open reclaim candidates, attempt-cap abandon candidates, abandoned/quarantined terminal review rows, reset-history claimed rows, completed-row audit exposure, and `--selftest-sync-domain-model`.
- rev0696: historical source/audit only in this package; the rev0696 runnable binary is intentionally omitted. `bin/rev0696/anonsync_core-linux-x86_64-gcc-openssl3-sqlite3` — release build containing evidence-preserving terminal reset for abandoned/quarantined resume-transfer workorders, durable reset events, quarantine history, retry-at backoff scheduling, attempt-cap terminal abandon policy, previous-owner reclaim event history, lease-timed non-stealing workorders, and `--selftest-sync-domain-model`.
- rev0695: historical source/audit only in this package; the rev0695 runnable binary is intentionally omitted. `bin/rev0695/anonsync_core-linux-x86_64-gcc-openssl3-sqlite3` — release build containing durable quarantine for mismatched claimed resume-transfer workorder evidence, retry-at backoff scheduling, attempt-cap terminal abandon policy, previous-owner reclaim event history, lease-timed non-stealing workorders, and `--selftest-sync-domain-model`.
- rev0694: historical source/audit only in this package; the rev0694 runnable binary is intentionally omitted. `bin/rev0694/anonsync_core-linux-x86_64-gcc-openssl3-sqlite3` — release build containing deterministic retry-at backoff scheduling for resume-transfer workorders, retry-window-gated expired reclaim, attempt-cap terminal abandon policy, previous-owner reclaim event history, lease-timed non-stealing workorders, and `--selftest-sync-domain-model`.
- rev0693: historical source/audit only in this package; the rev0693 runnable binary is intentionally omitted. `bin/rev0693/anonsync_core-linux-x86_64-gcc-openssl3-sqlite3` — release build containing attempt-cap terminal abandon policy for expired resume-transfer workorders, previous-owner reclaim event history, lease-timed non-stealing workorders, and `--selftest-sync-domain-model`.
- rev0692: historical source/audit only in this package; the rev0692 runnable binary is intentionally omitted. `bin/rev0692/anonsync_core-linux-x86_64-gcc-openssl3-sqlite3` — release build containing previous-owner reclaim event history for expired resume-transfer claims, lease-timed non-stealing workorders, and `--selftest-sync-domain-model`.
- rev0691: historical source/audit only in this package; the rev0691 runnable binary is intentionally omitted. `bin/rev0691/anonsync_core-linux-x86_64-gcc-openssl3-sqlite3` — release build containing lease-timed resume transfer claims, expired workorder reclaim, non-stealing owned execution, and `--selftest-sync-domain-model`.
- rev0690: historical source/audit only in this package; the rev0690 runnable binary is intentionally omitted. `bin/rev0690/anonsync_core-linux-x86_64-gcc-openssl3-sqlite3` — release build containing split claim-only resume transfer workorders, non-stealing owned execution, and `--selftest-sync-domain-model`.
- rev0688: historical source/audit only in this package; the rev0688 runnable binary is intentionally omitted. `bin/rev0688/anonsync_core-linux-x86_64-gcc-openssl3-sqlite3` — release build containing durable worker-owned resume transfer workorder rows plus `--selftest-sync-domain-model`.
- rev0687: historical source/audit only in this package; the rev0687 runnable binary is intentionally omitted. `bin/rev0687/anonsync_core-linux-x86_64-gcc-openssl3-sqlite3` — release build containing the bounded resume-cycle drain executor plus `--selftest-sync-domain-model`.
- rev0686: historical source/audit only in this package; the rev0686 runnable binary is intentionally omitted.
- rev0685: historical source/audit only in this package; the rev0685 runnable binary is intentionally omitted.
- rev0684: historical source/audit only in this package; the rev0684 runnable binary is intentionally omitted.
- rev0683: historical source/audit only in this package; the rev0683 runnable binary is intentionally omitted.
- rev0682: historical source/audit only in this package; the rev0682 runnable binary is intentionally omitted.
- rev0681: historical source/audit only in this package; the rev0681 runnable binary is intentionally omitted.
- rev0680: historical source/audit only in this package; the rev0680 runnable binary is intentionally omitted.
- rev0679: historical source/audit only in this package; the rev0679 runnable binary is intentionally omitted.
- rev0678: historical source/audit only in this package; the rev0678 runnable binary is intentionally omitted.
- rev0677: historical source/audit only in this package; the rev0677 runnable binary is intentionally omitted.
- rev0676: historical source/audit only in this package; the rev0676 runnable binary is intentionally omitted.
- rev0675: historical source/audit only in this package; the rev0675 runnable binary is intentionally omitted.
- rev0674: historical source/audit only in this package; the rev0674 runnable binary is intentionally omitted.
- rev0673: historical source/audit only in this package; the rev0673 runnable binary is intentionally omitted.
- rev0672: historical source/audit only in this package; the rev0672 runnable binary is intentionally omitted.
- rev0670: historical source/audit only in this package; the rev0670 runnable binary is intentionally omitted.
- rev0669: historical source/audit only in this package; the rev0669 runnable binary is intentionally omitted.
- rev0668: historical source/audit only in this package; the rev0668 runnable binary is intentionally omitted.
- rev0667: historical source/audit only in this package; the rev0667 runnable binary is intentionally omitted.
- rev0666: historical source/audit only in this package; the rev0666 runnable binary is intentionally omitted.
- rev0665: historical source/audit only in this package; the rev0665 runnable binary is intentionally omitted.
- rev0664: historical source/audit only in this package; the rev0664 runnable binary is intentionally omitted.
- rev0663: historical source/audit only in this package; the rev0663 runnable binary is intentionally omitted.
- rev0662: historical source/audit only in this package; the rev0662 runnable binary is intentionally omitted.
- rev0661: historical source/audit only in this package; the rev0661 runnable binary is intentionally omitted.
- rev0660: historical source/audit only in this package; the rev0660 runnable binary is intentionally omitted.
- rev0659: historical source/audit only in this package; the rev0659 runnable binary is intentionally omitted.
- rev0658: historical source/audit only in this package; the rev0658 runnable binary is intentionally omitted.
- rev0657: historical source/audit only in this package; the rev0657 runnable binary is intentionally omitted.
- rev0656: historical source/audit only in this package; the rev0656 runnable binary is intentionally omitted.
- rev0655: historical source/audit only in this package; the rev0655 runnable binary is intentionally omitted.
- rev0654: historical source/audit only in this package; the rev0654 runnable binary is intentionally omitted.
- rev0653: historical source/audit only in this package; the rev0653 runnable binary is intentionally omitted.
- rev0652: historical source/audit only in this package; the rev0652 runnable binary is intentionally omitted.
- rev0651: historical source/audit only in this package; the rev0651 runnable binary is intentionally omitted.

Historical source, fixtures, manifests, validators, and audit logs remain in the package for review; historical binaries are intentionally omitted.
