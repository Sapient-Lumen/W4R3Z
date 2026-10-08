# Process control and prompts

VHK now includes a small set of Linux-native “automation glue” steps so macros
do not have to shell out for every confirmation dialog or background program.

## Prompt steps

VHK prefers common desktop dialog helpers when available:
- `zenity`
- `yad`
- `kdialog`
- `dialog` (text UI)

If none are available, the runner falls back to simple console interaction.

Supported steps:
- `ShowMessage`
- `AskYesNo`
- `InputBox`
- `ChooseFromList`

These are useful for “confirm before destructive step”, “ask user for a search
term”, or “pick one of several windows/files/workspaces” style flows.

## Process steps

Supported steps:
- `StartProcess`
- `WaitForProcessExit`
- `KillProcess`

`StartProcess` is intentionally separate from `RunShell`:
- `RunShell` = run a shell command synchronously and capture its result
- `StartProcess` = launch asynchronously and expose a PID for later steps

Example:

```yaml
- type: StartProcess
  command: ["python3", "-m", "http.server", "8765"]
  out_pid: server_pid

- type: AskYesNo
  text: "Stop the temporary server?"
  out_var: should_stop

- type: If
  condition: "should_stop"
  then_steps:
    - type: KillProcess
      pid: "${server_pid}"
      signal: TERM
      wait_ms: 500
```

## Diagnostics

`vhk doctor` now reports detected dialog helpers alongside the existing input,
screenshot, clipboard, and notification backends.
