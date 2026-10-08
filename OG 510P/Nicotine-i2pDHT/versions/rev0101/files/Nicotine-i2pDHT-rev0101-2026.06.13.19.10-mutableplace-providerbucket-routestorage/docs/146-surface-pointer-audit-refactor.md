# Surface pointer audit/refactor

The cube is now large enough that wake-from-amnesia files can drift. rev0018 adds `surfaceaudit.py` for gentle JSON surface checks:

- missing `PUBLIC_SURFACE.json` entry paths;
- missing `HEAD_REGISTRY.json` head paths;
- revision-string absence in living surfaces;
- info-level notes where a head key starts acting like a revision label.

This is separate from `scripts/evidence/check_surfaces.py`, which remains fail-closed for the current public surface. The audit is meant to expose design debt without making every historical wart block iteration.

`cubeaudit.py` also got a small refactor: VERSION/pyproject/README checks now run only when the audited root looks like a full cube, so temporary duplicate-fixture tests stay focused on supersession behavior.
