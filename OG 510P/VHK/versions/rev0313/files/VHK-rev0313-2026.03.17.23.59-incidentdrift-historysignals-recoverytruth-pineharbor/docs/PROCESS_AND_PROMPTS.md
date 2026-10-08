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
- `PromptForm`
- `ChooseFromList`

These are useful for “confirm before destructive step”, “ask user for a search
term”, “collect several related parameters before launch”, or “pick one of
several windows/files/workspaces” style flows.

`ChooseFromList` is more launcher-oriented than the other prompt steps. For a
single selection it now prefers the native “type-to-filter” picker style people
already use on Linux desktops:
- X11: `rofi`, then `dmenu`
- Wayland: `fuzzel`, then `tofi`, then `wofi`
- fallback: dialog helpers and finally console interaction

That keeps chooser-style macros closer to the Linux ecosystem instead of
forcing every selection through a generic dialog box. You can override the
automatic choice with `VHK_CHOOSER_BACKEND=<name>` when you want a specific
picker.

`PromptForm` is the first step toward native “macro forms”. It prefers YAD's
multi-field form dialog on Linux when available and otherwise degrades to a
portable sequence of per-field prompts.

Example:

```yaml
- type: PromptForm
  title: "Deploy release"
  text: "Collect release parameters"
  out_var: form
  fields:
    - name: version
      label: Version
      default: "1.2.3"
    - name: environment
      label: Environment
      kind: choice
      choices: [dev, staging, prod]
    - name: confirm
      label: Ship now?
      kind: bool
      default: true

- type: Log
  message: "Deploying ${form.version} to ${form.environment}"
```

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

`vhk doctor` now reports both dialog helpers and chooser helpers alongside the
existing input, screenshot, clipboard, and notification backends.


## Project palette

The same chooser stack now powers a project-level launcher surface:

```bash
vhk palette /path/to/project
```

This is intentionally simple but useful:
- recent-first ordering by default using recent run history
- launcher-first UI on graphical sessions
- `--json` output for future Studio surfaces or external launchers
- `--no-run` when you only want the chosen macro name

That gives VHK a real Linux-native macro palette without waiting for a full GUI Studio.


## Preset-attached prompt overlays

Macros can now attach a `prompt_form` directly to a saved preset. This is useful
when the macro itself should stay generic but a launcher action still needs a few
values at run time.

Example:

```yaml
name: deploy_release
presets:
  - name: prod
    vars:
      env: prod
      approve: true
    prompt_form:
      title: Deploy ${env}
      text: Collect release details
      fields:
        - name: version
          label: Version
        - name: ticket
          label: Ticket
steps:
  - type: Log
    message: "Deploying ${version} to ${env} (ticket=${ticket})"
```

Merge order is intentional:

1. preset `vars:`
2. CLI `--vars`
3. prompt answers

That lets launcher actions stay reusable without cloning a whole macro just to
collect version numbers or ticket ids.

## Remembered answers and prompt profiles

`PromptForm` steps and preset-attached `prompt_form` overlays now support a
project-local answer store at `.vhk/prompt_profiles.json`.

- last-used answers are loaded automatically on the next run
- `vhk run ... --prompt-profile NAME` loads a named profile
- `vhk run ... --save-prompt-profile NAME` saves submitted answers under that name
- `vhk palette ...` supports the same profile flags
- password fields are never persisted
- individual fields may opt out of persistence with `remember: false`

By default, VHK auto-derives a profile key per prompt location (`macro + out_var`
for `PromptForm`, `macro + preset` for preset overlays). Authors can override
that with `profile_key:` when they want multiple prompts to share the same
remembered values.
