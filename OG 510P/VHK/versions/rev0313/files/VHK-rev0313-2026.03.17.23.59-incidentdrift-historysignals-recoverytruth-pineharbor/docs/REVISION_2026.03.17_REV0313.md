# REV0313 — Installed incident-signature drift

This revision extends the installed-lane status bridge with one more Linux-native
operator truth: **incident-signature drift**.

The launcher already classified the current incident as a clean session skip,
condition skip, start-limit churn, service failure, missing-unit loss,
probe/runtime breakage, quiet no-recent-incident, or unavailable. REV0313 adds a
bounded local history for those incident snapshots and threads one drift verdict
through installed status, support docs, host rehearsal, and host dossier output.

Added:
- `src/vhk/project/session_incident_drift.py`
- installed `STATUS_INCIDENT_HISTORY` in the generated native launcher
- installed status JSON/Markdown `service.incident_drift`
- support docs/checklists showing incident-drift verdicts
- rehearsal/dossier evidence capture and report rendering for incident drift

New incident-drift verdicts:
- `first_snapshot`
- `stable`
- `changed_recently`
- `recovered_to_quiet`
- `drifted_from_quiet`
- `changed_skip_mode`
- `changed_incident_mode`
- `chronic_start_limit`
- `chronic_service_failure`
- `chronic_missing_unit`
- `chronic_probe_error`
- `flapping_incidents`
- `unavailable`
