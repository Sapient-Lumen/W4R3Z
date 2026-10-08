# Editor registration groups

Micromax-editor already had two useful ideas:

- commands can be defined from micromax (`ed.cmd-add`)
- keybindings can be installed from micromax (`ed.bind`)

Rev34 adds a tiny but important layer on top: **registration groups**.

## Why

During plugin development, reloadability matters more than elegance.
If a plugin adds a command or a binding during `init`, then gets reloaded a few
times, stale registrations can survive unless the editor knows which ones came
from that plugin.

A string group tag is the cheap answer.

It gives us:

- batch cleanup on unload/reload
- better introspection for `showcmd` / `showkey`
- a stable machine-readable surface for future tools and LLMs

## Surface

Hostcalls:

```forth
ed.group!         ( group|0 -- )
ed.group@         ( -- group|0 )
ed.cmd-rows       ( -- [[name doc group|0 [file line col]|0] ...] )
ed.binding-detail ( -- [[key action-spec group|0 [file line col]|0] ...] )
```

Existing hostcalls now *use* the current group when present:

```forth
ed.cmd-add ( xt name doc -- ok )
ed.bind    ( key action-spec -- )
```

## Example

```forth
: hello-cmd ( args -- ok )
  drop
  "hello" "ed.msg" hostcall
  1
;

"plugin:demo" "ed.group!" hostcall
' hello-cmd "hello" "print hello" "ed.cmd-add" hostcall
"Ctrl-h" "command:hello" "ed.bind" hostcall
0 "ed.group!" hostcall
```
Note: this manual grouping example is for trusted/user code. Plugin source and
lifecycle hooks already run under a loader-owned `plugin:<name>` group; since
rev0862, plugin-originated code cannot clear or change that group before
registering callbacks.


Now the editor can report:

- `help hello` / `showcmd hello`
- `showkey Ctrl-h`

and include both provenance and group metadata when available.

## Plugin loader integration

The reference `PluginManager` now evaluates plugin source and lifecycle words
with:

```text
vm.current_editor_group = "plugin:<name>"
```

On unload/reload it removes every command/binding in that group.
This makes plugin reload much less leaky without requiring whole-VM resets.

## Design note

This is intentionally smaller than a full mode/layer system.
Groups are not keymap modes. They are just metadata + cleanup tags.

That is a feature, not a bug:

- today: reload-safe cleanup and better debugging
- later: reusable substrate for modes/layers/transient maps
- missing `showcmd NAME` lookups now fail plainly as `showcmd: no such command: NAME`, so command registration inspection keeps the same explicit dialect even on a miss
- Micromax-defined commands registered through `ed.cmd-add` now also keep the command name visible on faults as `command NAME: error: ...`, so reloadable/plugin-defined commands debug in the same dialect as built-in commands
