# Software accountability fields

Rev0011 adds a non-schema-enforced but lint-checked payload block for software accountability records:

```json
"software_accountability_fields": {
  "internal_state_surface": "What software/system state mattered but was not visible to affected outsiders?",
  "external_attribution_surface": "What output, symptom, legal claim, compliance result, or operator action carried attribution?",
  "investigation_or_detection_surface": "What later made the hidden state partially visible?",
  "corrective_or_legal_surface": "What correction, enforcement, recall, appeal, inquiry, redress, or recommendation followed?"
}
```

These fields are deliberately separate from the older rev0010 software-failure fields (`change_surface`, `validation_boundary`, `warning_surface`, `blast_radius`, `rollback_or_recovery`). A control-plane outage and a machine-testimony attribution trap overlap, but they are not the same phenomenon.
