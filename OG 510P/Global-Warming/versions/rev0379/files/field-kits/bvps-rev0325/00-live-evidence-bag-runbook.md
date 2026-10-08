# BVPS rev0325 live evidence-bag runbook

Use this before and during the exercise window. Preserve the original artifact before redaction. Hash the original. Create a redacted public surrogate only after the original hash and custody event exist. A bag accepted by the cube is never a readiness closure by itself.

Minimum command pattern:

```bash
python tools/build_nuclear_emergency_bvps_evidence_bag_rev0325.py \
  --input-dir /path/to/evidence \
  --output-dir /path/to/bags \
  --bag-id BVPS-YYYYMMDD-ROLE-001 \
  --site-or-overlay BVPS_ANON_EXERCISE \
  --packet-id PKT-ALERT-LOG-001
```
