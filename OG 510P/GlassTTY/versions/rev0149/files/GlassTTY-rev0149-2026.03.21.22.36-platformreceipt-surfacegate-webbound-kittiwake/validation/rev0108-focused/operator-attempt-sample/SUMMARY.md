# GlassTTY operator attempt

- label: sample-attempt
- status: finished
- started_at: 2026-03-18T01:44:08Z
- finished_at: 2026-03-18T01:44:08Z
- outcome: success
- planned_command: `python scripts/validate-release.py --out-dir validation/latest --resume`

## Before

- readiness_grade: `blocked-by-validation`
- primary_next_kind: `resume_validate_release`
- primary_next_command: `python scripts/validate-release.py --out-dir validation/latest --resume`
- best_profile_name: `main`
- validation_complete: `False`
- validation_running_step_name: `pytest_cli`

## After

- readiness_grade: `live-lane-ready`
- primary_next_kind: `capture_validate_release`
- primary_next_command: `python scripts/validate-release-capture.py --source-dir validation/latest --output-dir validation/latest/validate-release-capture`
- best_profile_name: `main`
- validation_complete: `True`
- validation_running_step_name: `None`

## Attempt diff

- summary: operator attempt changed the next-action surface
- changed_fields: readiness_grade, primary_next_kind, primary_next_command, validation_complete, validation_running_step_name

## Commands

- report: `python scripts/operator-attempt.py --pretty`
- start_latest: `python scripts/operator-attempt.py start --output-dir validation/latest/operator-attempt`
- finish_latest: `python scripts/operator-attempt.py finish --output-dir validation/latest/operator-attempt --outcome success`
- history: `python scripts/operator-attempt.py history --pretty`

## History

- history_count: 1
- history_summary: no previous operator attempt exists yet
