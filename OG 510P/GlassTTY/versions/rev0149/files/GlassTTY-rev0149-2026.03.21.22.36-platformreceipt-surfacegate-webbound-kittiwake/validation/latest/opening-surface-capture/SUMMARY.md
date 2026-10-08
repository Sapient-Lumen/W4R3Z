# Opening surface conformance

- generated_at: 2026-03-21T22:05:00Z
- all_valid: True
- required_read_count: 5
- required_command_count: 3
- warning_count: 0

## Required reads

- `README.md` — exists=True, mentioned_in_startup_doc=True
- `STATUS.md` — exists=True, mentioned_in_startup_doc=True
- `REVISION-RECEIPT.json` — exists=True, mentioned_in_startup_doc=True
- `PROJECT_MAP.md` — exists=True, mentioned_in_startup_doc=True
- `docs/operator-startup.md` — exists=True, mentioned_in_startup_doc=True

## Required commands

- `python scripts/doctor.py --pretty` — mentioned_in_startup_doc=True
- `python scripts/readiness-report.py --pretty` — mentioned_in_startup_doc=True
- `python scripts/check-opening-contract.py --pretty` — mentioned_in_startup_doc=True
