# Daemon

The Python daemon currently has two closely related roles:

1. native messaging host for Chromium
2. local broker and CLI state owner

## Entrypoints

- `python -m glassttyd.native_host`
- `python -m glassttyd.cli ping`
- `python -m glassttyd.cli socket-status`
- `python -m glassttyd.cli watch`

## Local paths

By default GlassTTY uses:

- state root: `~/.local/share/glasstty/state`
- run dir: `~/.local/share/glasstty/run`
- broker socket: `~/.local/share/glasstty/run/daemon.sock`

## Import path

During development, either:

```bash
export PYTHONPATH="$PWD/daemon/src"
```

or install the package:

```bash
pip install -e daemon
```
