# REV0309 — installed startup handoff verdicts

Date: 2026-03-17

## Summary

This revision extends the installed-lane status/support story so VHK can report
**startup ownership truth** in addition to session readiness and runtime health.
The native launcher status JSON/Markdown now preserves one startup-handoff
verdict derived from user-unit enablement plus effective XDG autostart state.

## Added

- `src/vhk/project/startup_handoff_status.py`
- `tests/test_startup_handoff_status.py`
- `docs/NOTE_2026.03.17_INSTALLED_STARTUP_HANDOFF_STATUS.md`
- `docs/RESEARCH_2026.03.17_INSTALLED_STARTUP_HANDOFF_STATUS.md`

## Updated

- `src/vhk/project/native_install_pack.py`
- `src/vhk/project/support_pack.py`
- `tests/test_native_install_pack_cli.py`
- `tests/test_support_pack_cli.py`
- `README.md`
- `docs/SPECS.md`
- `docs/PLAN_2026.03.17_LINUX_NATIVE_AHK_PARITY.md`
- `docs/ISSUES_2026Q1.md`

## New startup-handoff verdicts

- `manual_or_external_owner`
- `primary_user_unit_owner`
- `fallback_autostart_owner`
- `duplicate_start_risk`
- `autostart_hidden_no_owner`
- `autostart_tryexec_missing`
- `masked_no_owner`
- `no_startup_owner`
- `unavailable`

## Validation

Focused tests passed for:

- `tests/test_startup_handoff_status.py`
- `tests/test_native_install_pack_cli.py`
- `tests/test_support_pack_cli.py`
- `tests/test_service_compose_pack_cli.py`
- `tests/test_host_rehearsal_pack_cli.py`
- `tests/test_host_dossier_pack_cli.py`
- `tests/test_setup_pack_cli.py`
- `tests/test_release_stage_pack_cli.py`
