# rev0007 refactor and audit

## Refactor

Added a dedicated table layer:

```text
src/muc5/gametable.py
```

This prevents CLI/table logic from leaking into the referee engine. The engine still owns legality and state transitions; the table owns rendering, external-seat pausing, and save/resume.

Added a small agent factory:

```text
src/muc5/agents.py::make_agent
```

This keeps scripts from hard-coding class constructors.

## Audit checks added

`scripts/audit_cube.py` now checks:

```text
rev0007 gametable starts and stops at external seat
rev0007 external action can be applied and serialized
rev0007 sample table artifacts exist
rev0007 sparring-agent probe has 512 rows and summary games=512
rev0007 required files are present
```

## Validation run

Expected validation commands:

```bash
python -m pytest -q
python run_smoke.py
python scripts/run_rev0007_sparring_probe.py
python scripts/audit_cube.py
```

