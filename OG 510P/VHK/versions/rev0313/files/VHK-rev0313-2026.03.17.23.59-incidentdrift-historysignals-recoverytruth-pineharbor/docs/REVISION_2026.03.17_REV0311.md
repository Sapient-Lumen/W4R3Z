# REV0311 — installed runtime-health drift

This revision teaches the installed lane to keep a bounded runtime-health
history in `VHK_RUNTIME_HEALTH_HISTORY.json` and to summarize that history as a
runtime-health drift verdict. That summary now appears in the native installed
status bridge, the support pack, the host rehearsal report, and the host
dossier.

Key additions:
- `src/vhk/project/session_runtime_health_drift.py`
- installed launcher status now writes `VHK_RUNTIME_HEALTH_HISTORY.json`
- `service.runtime_health_drift` in installed `--status-json`
- support/rehearsal/dossier docs now surface runtime-health drift alongside
  readiness, runtime-health, startup-handoff, and startup-handoff drift
