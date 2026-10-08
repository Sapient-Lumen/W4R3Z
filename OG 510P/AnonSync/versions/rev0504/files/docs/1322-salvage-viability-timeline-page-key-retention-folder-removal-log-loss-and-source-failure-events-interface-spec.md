## Salvage-viability timeline

### Purpose
Show how future rescue strength changed over time instead of pretending the latest encrypted-backup state has always meant the same thing.

### Timeline events to preserve
- RW / RO keys escrowed or lost.
- Encrypted node first created.
- Folder removed, disconnected, re-added, or rebound.
- Storage root or service account changed.
- Logs retained, rotated away, or exported.
- Archive enabled / disabled or delete-state convergence observed.
- Source peer healthy, degraded, or failed.
- Recovery lane attempted, succeeded, failed, or became unknown.

### Per-event fields
- **Event type**
- **What changed in salvage floor**
- **What prerequisite improved or degraded**
- **What stronger rescue sentence became newly blocked or newly allowed**

### Output sentence
At any review point the operator should be able to read one timeline summary that says: `salvage was plausible from this date, weakened here when continuity changed, weakened again when locator evidence was lost, and is currently only honest through this named lane.`
