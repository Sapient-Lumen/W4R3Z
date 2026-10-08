# BVPS rev0360 one-command go/no-go runbook

Run from the package root:

```bash
python3 tools/run_nuclear_emergency_bvps_eventday_gonogo_rev0360.py --root . --out cube/nuclear-emergency-bvps-gonogo-run-result-rev0360.csv
```

Expected successful operator state: **capture-ready / claim-frozen**.  
Forbidden interpretation: **ready, green, passed, safe, sufficient, demonstrated, or closed**.

A real or anonymized packet still moves only to quarantine and then adjudication. It cannot close readiness automatically.
