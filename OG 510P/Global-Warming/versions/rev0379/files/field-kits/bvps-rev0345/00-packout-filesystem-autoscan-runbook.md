# BVPS rev0345 packout filesystem autoscan runbook

Run:

```bash
python tools/scan_nuclear_emergency_bvps_packout_filesystem_rev0345.py --root . --write
python tools/validate_nuclear_emergency_bvps_packout_autoscan_rev0345.py --root .
```

Folder present = ready to receive evidence. Payload with hash/custody/redaction/QA = candidate for adjudication. Candidate is not closure. Empty skeleton = active loss cap.
