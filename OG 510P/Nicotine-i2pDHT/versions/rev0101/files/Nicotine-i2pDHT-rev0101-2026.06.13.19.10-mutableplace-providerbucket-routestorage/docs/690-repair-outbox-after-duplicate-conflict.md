# Repair outbox after duplicate conflict

`repairoutbox.py` stages repair publication after remote duplicate conflict evidence.

A remote conflict does not permit a blind retry. The repair outbox requires:

```text
delivery_repair_mesh_report.repair_required
remote_witness_ledger_report.conflict_memory
same exact boundary
marker sequence / previous-link discipline
marker family/path diversity
component digest binding
no hard-negative pressure
```

The outbox can stage:

```text
withdraw_duplicate_public_record
publish_repair_notice
```

This remains no-network. The marker is not a live write; it is a local staged intent that a later side-effect boundary may accept or suppress.

The important negative path is just as important as the positive one: if remote witnesses say the duplicate was benign, the repair outbox holds `no_repair_required` instead of manufacturing work.
