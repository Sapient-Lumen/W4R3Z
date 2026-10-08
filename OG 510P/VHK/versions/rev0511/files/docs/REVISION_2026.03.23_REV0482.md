# Revision 0482 — shipped self-install and smoke-rehearsal into the flagship i3/X11 stack

This revision makes the generated flagship stack deployable on its own instead of requiring manual copying.

## What changed

- Added `src/vhk/project/i3_x11_flagship_stack_install_pack.py`
- Added `tests/test_i3_x11_flagship_stack_install_pack.py`
- Added `docs/DECISION_2026.03.23_FLAGSHIP_STACK_SELF_INSTALL.md`
- Added root-level generated flagship-stack scripts:
  - `install_user_session.sh`
  - `uninstall_user_session.sh`
  - `smoke_install.sh`
- Updated `vhk gen-i3-busd-stack` so those scripts are emitted, executable, and listed in the generated README/artifact summary.
- Updated `control-plane.json` so the install/uninstall/smoke entrypoints are machine-readable and so the manifest now includes `flagship_install_summary`.
- Expanded the startup-bridge helper contract so install/smoke entrypoints are part of the explicit stack story.

## What the install layer does

The generated install script now copies:

- the socket/service units into `~/.config/systemd/user/`
- the generated wrappers and `control-plane.json` into `~/.config/vhk/<unit>/session-service/`
- the generated i3 snippet into `~/.config/i3/vhk/<unit>.conf`
- the autostart bridge only when `VHK_INSTALL_AUTOSTART_BRIDGE=1`

The smoke script rehearses that whole path into a throwaway XDG root with `VHK_SKIP_SYSTEMCTL=1`, then uninstalls again.

## Why

Revision 0481 made the startup bridge real. Revision 0482 makes the stack itself landable.

That sharpens the repo in the same direction:

- resident user-service lane is easier to install and roll back
- startup-owner changes are easier to rehearse safely
- private-LLM/operator control planes gain stable deploy/retire entrypoints
- manual copy/paste drift is reduced

## Tests

- `python -m py_compile src/vhk/cli.py src/vhk/project/i3_x11_flagship_startup_bridge.py src/vhk/project/i3_x11_flagship_stack_bridge_pack.py src/vhk/project/i3_x11_flagship_stack_install_pack.py tests/test_i3_x11_flagship_startup_bridge.py tests/test_i3_x11_flagship_stack_bridge_pack.py tests/test_i3_x11_flagship_stack_install_pack.py tests/test_i3_busd_stack_cli.py`
- `pytest -q tests/test_i3_x11_flagship_startup_bridge.py tests/test_i3_x11_flagship_stack_bridge_pack.py tests/test_i3_x11_flagship_stack_install_pack.py tests/test_i3_busd_stack_cli.py tests/test_service_compose_pack_cli.py`
- manual local generation of a flagship stack plus execution of the generated `smoke_install.sh`
