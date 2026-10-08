# U-269 handler-level proof packet

Contents:

```text
../../tools/probe_rev0009_u269_upload_completion_lifetime.py
../../evidence/rev0009-u269-upload-completion-lifetime-probe.jsonl
../../evidence/rev0009-u269-source-trace.md
```

rev0009 result across all three source lanes:

```text
all_bytes_progress_keeps_transfer_active: True
no_finish_on_all_bytes_progress_alone: True
control_close_finishes: True
```

Interpretation: the handler-level behavior is real, but this item was not promoted strict because public upload-progress/completion/stuck-transfer history is adjacent, and the network layer's idle timeout likely bounds the lifetime unless the peer continues activity. Keep U-269 as a backlog hardening/regression-test candidate unless a later full network-loop harness shows stronger resource retention.
