# 2026-03-25 — userspace failure resume pass

## Goal

Add one compact later-machine failure-decoder surface so the first real Rust failure log can be turned into an immediate resume decision instead of a full-stack reopen.

## Added

- `scripts/report/build_cloudtainer_userspace_failure_resume_card.py`
- `scripts/tools/classify_cloudtainer_userspace_failure.py`
- `scripts/test/check_cloudtainer_userspace_failure_resume_card.py`
- `artifacts/reports/cloudtainer_userspace_failure_resume_card.json`
- `docs/CLOUDTAINER_USERSPACE_FAILURE_RESUME_CARD.md`

## Main preserved result

- failure resume code: `phase_scoped_resume_tripwire`
- preserved failure classes: `8`
- structured capture variants: `3`
- exact witness anchor still: `lift_fsm_strategy_family_lift_first_seed`
- quick foothold target still: `probe_run`

## Why this mattered

The archive already preserved how to bootstrap userspace rustup later, how small the fetch and compile surfaces still are, and the exact offline proof ladder.
What it still did **not** preserve was the next thing a human would ask after the first real Rust attempt failed: *which phase just failed, and where do I resume without reopening everything?*
This pass closes that gap.

## Validation run

- `make update-cloudtainer-userspace-failure-resume-card`
- `make test-cloudtainer-userspace-failure-resume-card`
- `make update-command-inventory`
- `make test-command-inventory`
- `make update-validator-inventory`
- `make test-validator-inventory`
- `python3 scripts/test/check_generated_docs_presence.py`
- `python3 scripts/test/check_readme_command_surface.py`
- `python3 scripts/test/check_docs_index_core.py`
- `python3 scripts/test/check_research_docs.py`
- `python3 -m py_compile scripts/report/build_cloudtainer_userspace_failure_resume_card.py scripts/tools/classify_cloudtainer_userspace_failure.py scripts/test/check_cloudtainer_userspace_failure_resume_card.py`

## Source handles added

- `RS-GR-566` — Cargo external-tools JSON messages
- `RS-GR-567` — Cargo test message-format options
