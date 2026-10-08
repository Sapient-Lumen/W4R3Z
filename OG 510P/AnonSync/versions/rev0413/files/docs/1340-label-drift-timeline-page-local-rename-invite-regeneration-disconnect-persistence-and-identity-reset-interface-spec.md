## Label-drift timeline

### Purpose
Keep naming drift legible over time instead of letting several unrelated labels collapse into one remembered `name`.

### Timeline events that must stay visible
- local filesystem rename on one device
- local desktop alias edit
- invite-specific label regeneration for link or QR
- disconnect while preserving old local alias in UI
- reset back to default disk-based name
- device-label edit on mobile
- identity unlink and new-name regeneration
- derived backup-folder creation using platform-specific naming rules

### Drift warnings
- same displayed text across two planes does not prove same meaning
- same identity text with a different fingerprint does not prove continuity
- same share alias after disconnect does not prove current connection still exists
- different invite labels do not prove different shares
- backup-folder names derived from device class or device name are weaker than share identity proof
