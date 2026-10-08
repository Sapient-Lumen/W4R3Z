# ADR 0079 — version audit applies to full cubes, not small fixtures

## Decision

VERSION/pyproject/README consistency belongs to full-cube audits. Small temporary supersession fixtures should not fail or warn merely because they do not include a full release surface.

## Consequences

`cubeaudit.py` now runs the version-surface check only when the audited root looks like a cube. This preserves the audit value while keeping narrow tests narrow.
