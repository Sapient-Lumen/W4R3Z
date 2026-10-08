# Research — picker-native chooser lanes and script-mode protocols

## Question

What should VHK learn from current Linux launcher/picker tools beyond the
already captured “large macro catalogs want launcher hubs” lesson?

## Takeaway

The sharper lesson is that Linux picker tools are not just generic launchers.
They are a real **chooser protocol layer**.

The current ecosystem keeps reinforcing the same shape:

- rofi separates script mode from dmenu mode and treats script mode as an
  explicit extension surface
- fuzzel keeps a general-purpose `--dmenu` picker lane for Wayland-class
  sessions
- wofi keeps a dmenu mode too, but as a wlroots-shaped launcher that still
  expects layer-shell or a `--normal-window` fallback depending on the session

That combination suggests a clear product lesson for VHK:

- chooser UIs should stay thin
- one stable action/entry-id catalog should feed them
- the real macro runtime should stay in VHK, not inside per-desktop picker glue

## Why this matters for VHK

Before this revision, VHK already had:

- `ChooseFromList` and prompt-aware runtime steps
- a project palette
- launcher-script export
- rofi custom-mode export

But the planner still under-modeled that whole surface. Prompt-rich projects
could look like they had “a palette” without the plan ever admitting that Linux
already has strong searchable chooser shells for this shape.

That was not creative enough and not honest enough.

## Product conclusion

So the planner should reason explicitly about:

- whether a project has prompt-rich or preset-rich workflows
- whether those flows are healthier as searchable chooser entry points than as
  another global bind
- whether launcher-script / rofi-mode exports should be surfaced as a real Linux
  control lane instead of leftover integration trivia

That leads to the product change in this revision:

- surface choices now include `picker-native-chooser`
- reference patterns now include `script-mode-picker-lane`
- ecosystem lessons now include `picker-protocol-thin-launch-surface`

## Practical hierarchy

For chooser-heavy Linux automation flows, the clearer hierarchy is:

1. stable VHK action catalog / palette entry ids
2. thin picker-native shells (launcher script, rofi mode, dmenu-style picker)
3. full macro execution inside VHK once a user selection is made

Those are different roles. Keeping them separate makes VHK feel more Linux-native
without pretending every desktop needs the same custom GUI.
