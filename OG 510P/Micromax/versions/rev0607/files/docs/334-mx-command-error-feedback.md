# Micromax-defined command error feedback

Rev392 tightens one small but high-leverage seam in the live scripting surface:
commands registered through `ed.cmd-add` now fail in the same typed dialect as
built-in editor commands.

## Why

By rev388, native command-bar commands already reported unexpected failures as:

- `command NAME: error: DETAILS`

But the bridge used by `ed.cmd-add` still lagged behind in two ways:

- unexpected host/runtime faults fell back to `mx command NAME error: DETAILS`
- Micromax faults like stack underflow skipped the command name entirely and
  only emitted raw `vm.format_error(...)` output

That made script-defined commands slightly harder to debug in logs and easier to
misread as a lower-tier surface than built-in commands.

## Change

The `ed.cmd-add` wrapper now prefixes both kinds of failure the same way:

- `command NAME: error: DETAILS`

For Micromax faults, the formatted VM error is preserved after the prefix, so
source spans, excerpts, and traces still appear.

Example:

- `command bad: error: <mx-test>:1:36: Stack underflow`
- `trace: bad-cmd`

## Why it matters

Micromax-defined commands are part of the real product surface, not a side
channel. If future plugins, keybindings, hooks, or command packs are built in
Micromax, their failures should remain as inspectable and searchable as the
native command dispatcher's failures.
