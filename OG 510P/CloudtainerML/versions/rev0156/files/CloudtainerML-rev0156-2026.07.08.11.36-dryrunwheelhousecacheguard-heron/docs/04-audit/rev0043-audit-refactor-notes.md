# rev0043 audit/refactor notes

The audit refactor is intentionally narrow:

- add `tools/attention_workload_audit.py`;
- teach `current_scientific_run_audit.py` to verify QK/softmax/V output guard fields;
- teach `evidence_integrity_audit.py` that the attention-output blocker is partially addressed but kernel timing and real traces remain blockers;
- update `smoke_validate.py` with an `attention_workload_repair` revision kind.

This is not a registry expansion. It is a semantic check that prevents the cube from treating selector exactness as attention-quality evidence.
