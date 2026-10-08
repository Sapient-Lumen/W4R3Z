# Retry settlement and withdraw repair

Retry attempts settle independently from the original send. rev0063 supports three local settlement shapes:

```text
retry_delivered
retry_aborted_by_late_ack
withdraw_repaired
```

A late ACK plus retry-delivered marker is quarantined unless the egress journal explicitly preserves contradiction evidence from an external branch. Withdraw repair has its own publication-memory lane so a withdraw-ready egress report is not automatically terminal.

Audit needles: retry settlement, withdrawrepair, retrysettlement.
