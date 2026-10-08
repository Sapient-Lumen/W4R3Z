# operator handoff summary

- captured_at: 2026-03-18T19:59:56Z
- readiness_grade: blocked-by-validation
- primary_next_kind: resume_validate_release
- primary_next_command: `python scripts/validate-release.py --out-dir validation/latest --resume`
- validation_complete: False
- validation_running_step_name: None
- smoke_report_timestamp: 2026-03-08T01:28:01Z
- best_profile: None
- artifact_count: 25
- copied_artifact_count: 17
- missing_required_artifact_count: 0
- history_count: 2
- comparison_summary: operator handoff matches the previous one on tracked fields

## commands

- operator_handoff_report: `python scripts/operator-handoff.py --pretty`
- operator_handoff_capture: `python scripts/operator-handoff.py capture --output-dir validation/latest/operator-handoff`
- operator_handoff_history: `python scripts/operator-handoff.py history --pretty`
- primary_next_command: `python scripts/validate-release.py --out-dir validation/latest --resume`

## copied artifacts

- static:README.md: `artifacts/README.md`
- static:ROADMAP.md: `artifacts/ROADMAP.md`
- static:PROJECT_MAP.md: `artifacts/PROJECT_MAP.md`
- static:STATUS.md: `artifacts/STATUS.md`
- static:TASKS.md: `artifacts/TASKS.md`
- static:DECISIONS.md: `artifacts/DECISIONS.md`
- static:MEMORY.md: `artifacts/MEMORY.md`
- static:.llm/README.md: `artifacts/.llm/README.md`
- static:.llm/SESSION_START.md: `artifacts/.llm/SESSION_START.md`
- static:.llm/SESSION_END.md: `artifacts/.llm/SESSION_END.md`
- static:.llm/WORKLOG.jsonl: `artifacts/.llm/WORKLOG.jsonl`
- docs:latest-handoff: `artifacts/docs/handoff-rev0109-2026-03-18.md`
- validation:latest-report: `artifacts/validation/latest/report.json`
- validation:latest-summary: `artifacts/validation/latest/SUMMARY.md`
- smoke:latest-report: `artifacts/validation/latest/e2e-fixturelab.json`
- readiness:capture-history: `artifacts/validation/readiness-report-captures.json`
- readiness:latest-capture-bundle: `artifacts/validation/rev0109-focused/readiness-report-capture`
