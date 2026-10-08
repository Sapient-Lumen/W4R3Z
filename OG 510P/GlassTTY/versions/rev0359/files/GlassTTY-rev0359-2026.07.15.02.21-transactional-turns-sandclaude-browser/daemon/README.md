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


## Receiver-operator commands

Useful receiver-audit commands now include:

- `python -m glassttyd.cli list-receivers --tab-id TAB_ID`
- `python -m glassttyd.cli resolve-receiver TAB_ID --active-outermost --ready-only`
- `python -m glassttyd.cli resolve-receiver TAB_ID --explain --first`

`--explain` adds resolver ranking details so a saved JSON artifact can show why one receiver won or why the result stayed ambiguous.
