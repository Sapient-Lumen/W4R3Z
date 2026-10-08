# Reference patterns (`vhk plan-project`)

`vhk plan-project` now emits `reference_patterns`.

This surface encodes a question that had been living mostly in prose:

> Which existing automation products or Linux-native tool shapes should this
> VHK project learn from right now?

Instead of leaving that answer in research notes only, the planner now scores a
small set of reusable product patterns and explains:

- what to borrow
- what to avoid
- why the pattern fits the current project shape
- which VHK commands support that direction

## Why this matters

VHK is trying to become Linux-native without forgetting why tools like
AutoHotkey and Pulover's Macro Creator were productive.

That means the project should not just chase backend parity. It should also
learn the *product shapes* that other tools got right:

- AHK-style runner/core ergonomics
- Pulover-style visual authoring and cleanup loops
- Espanso-style text/forms export
- WM/compositor bind shells
- remapper-layer offload (`keyd`, `kanata`, `KMonad`, `xremap`)
- portal/helper-boundary deployment on Wayland-class desktops

`reference_patterns` is the planner's first machine-readable attempt at that.

## Output shape

`vhk plan-project --json` now includes:

```json
{
  "reference_patterns": [
    {
      "id": "espanso-forms-text-tier",
      "title": "Espanso-style text/forms tier",
      "pattern_type": "text",
      "score": 82,
      "fit": "strong",
      "summary": "...",
      "borrow": ["..."],
      "avoid": ["..."],
      "evidence": ["..."],
      "commands": ["..."],
      "learn_from": ["Espanso"]
    }
  ]
}
```

## Initial patterns

The first revision includes six scored patterns:

1. `ahk-runner-core`
2. `pulover-visual-studio`
3. `espanso-forms-text-tier`
4. `wm-bind-dispatch`
5. `remap-daemon-offload`
6. `portal-helper-boundary`

These are intentionally broad. The goal is to help VHK answer:

- where should complexity live?
- what should remain in VHK core?
- what should move into exports, helpers, bundles, or remapper configs?
- which existing tools should we emulate for this specific project shape?

## Example

```bash
vhk plan-project ./myproj
vhk plan-project ./myproj --json
```

In the table view, the command now prints a **Reference patterns** section.
