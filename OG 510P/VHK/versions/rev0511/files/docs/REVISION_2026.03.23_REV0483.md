# Revision 0483 — installed-lane verify/repair for the flagship i3/X11 stack

## What changed

This revision turns the flagship stack's self-install story into a fuller day-2 deployment contract.

### Added top-level generated helpers

- `verify_user_session_json.sh`
- `verify_user_session.sh`
- `repair_user_session.sh`

### Tightened contracts

- `flagship_install_summary` now advertises the post-install helper set
- `flagship_startup_bridge_contract.helper_paths` now includes the new verify/repair surfaces
- the startup-bridge LLM/runtime-repair contract now points at the installed-lane verify/repair helpers first

### Runtime/control-plane changes

- `control-plane.json` now classifies the new helpers as snapshot / observability / actuation surfaces
- `smoke_install.sh` now rehearses install, verify, repair, and uninstall instead of only copy/remove
- `repair_user_session.sh` supports install-only rehearsal mode when `VHK_SKIP_SYSTEMCTL=1`

## Why it matters

The flagship lane is no longer only:

- generate
- install
- hope the resident runtime stays believable

It is now:

- generate
- smoke install
- install
- verify the installed lane with one machine-readable verdict
- repair with one bounded stack-local action when the installed lane drifted

That is a better fit for:

- i3/X11-first deployment reality
- session-bound warm service ownership
- private-LLM control loops that need one authoritative install verdict
- recorder/cleanup/replay-heavy projects where runtime trust must stay explicit

## Local verification

Focused checks passed locally:

- `pytest -q tests/test_i3_x11_flagship_startup_bridge.py tests/test_i3_x11_flagship_stack_install_pack.py tests/test_i3_busd_stack_cli.py tests/test_i3_x11_flagship_stack_bridge_pack.py tests/test_service_compose_pack_cli.py`
- generated-stack smoke install execution
- `python -m py_compile` on touched modules/tests
