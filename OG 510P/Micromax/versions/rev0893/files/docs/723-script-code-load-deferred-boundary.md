# Rev773 — script code-load and deferred-callback authority boundary

## Why this was risky

Rev772 blocked the obvious self-escalation path where a script used
`ed.command`, `ed.opt-set`, or immediate `set`/`toggle` to grant itself a
`cap.*` option.  A deeper audit found adjacent routes that still crossed the
same trust boundary:

- core Micromax `include`, `require`, `reload`, and `unrequire` still used the
  standalone VM loader from inside the editor VM;
- `ed.require` loaded files through `cap.fs-require`, but evaluated the loaded
  file outside `ed.script_context()`;
- `ed.run` executed action chains without entering script context, so
  `ed.run "command:set cap.fs-save true"` or `ed.run "mx:set cap.fs-open true"`
  could bypass the previous cap-mutation guard;
- script-originated timers and hook handlers could be registered while sandboxed
  and later execute outside the script context.

Those were all ways for delayed or nested script execution to become more
privileged than the original callback that created it.

## What changed

New module:

`src/micromax_editor/vm_load_policy.py`

New VM hooks:

- `VM.load_path_policy`
- `VM.load_source_reader`
- `VM.resolve_load_path_for_op(...)`
- `VM.read_load_source(...)`

The standalone VM keeps the old local-file behavior when those hooks are unset.
The editor installs hooks that are active only inside `ed.script_context()`.
When active, core `include` / `require` / `reload` / `unrequire` require
`cap.fs-require`; with `cap.fs-root` set, they search only contained candidates
and read through the contained file-recovery seam.

`ed.require` now evaluates the loaded source inside `ed.script_context()`, so
nested core loads and option mutations inherit the same reduced authority.

`plugin reload` command paths, the broad `reload` command, and the
`plugin.reload` hostcall now require `cap.fs-require` when invoked from script
context because they can evaluate code from disk.

`ed.run` now executes the requested action chain inside `ed.script_context()`.
That keeps `command:` and `mx:` action-chain branches aligned with `ed.command`
and `ed.press-key`.

`ed.macro-play` now replays direct hostcall requests inside `ed.script_context()`.
Interactive `macro play` is still a user-authority command, but script-triggered
macro replay cannot borrow ambient authority to run a recorded `set cap.*` step
before a gated operation.

Deferred callbacks now preserve their origin:

- `TimerTask.script_context` records whether `ed.after` was scheduled from
  script context;
- `HookHandler.script_context` records whether `hook-add` happened from script
  context;
- `Editor.pump_timers()` and `HookWord.execute()` re-enter script context for
  those script-originated callbacks.

Trusted user init/config evaluation and direct interactive VM evaluation remain
privileged: they can still set capabilities intentionally before running
capability-bearing commands.

## Concrete guarantees

- A script cannot use core `include` / `require` / `reload` / `unrequire` unless
  `cap.fs-require` is enabled.
- A file loaded by `ed.require` cannot mutate `cap.*` options merely because
  `ed.require` itself had authority to read/evaluate it.
- Nested core `require` calls inside an `ed.require`d file honor `cap.fs-root`
  and use contained reads.
- `ed.run "command:..."` and `ed.run "mx:..."` no longer escape the script
  option-mutation policy.
- `ed.macro-play` hostcalls no longer replay recorded command steps with ambient
  authority.
- Script-originated timers and hooks keep script authority when they run later,
  closing delayed self-escalation.
- Plugin reload command/hostcall surfaces are blocked from script context unless
  the caller has explicit code-load authority.

## Validation

Focused validation passed during the rev773 turn:

```text
42 require/script-cap tests passed in 3.38s
152 file/script/plugin capability tests passed in 3.78s
32 script-context file/action/macro boundary tests passed in 1.24s
155 macro/core/plugin picker/hostcall tests passed in 5.16s
88 focused boundary/doctor/plugin tests passed in 6.79s
```

The default doctor lane was expanded to include the timer/hook boundary tests.

## Remaining risk

This is still an application-level trust boundary, not an OS sandbox. Trusted
plugin loading remains privileged extension loading. The next worthwhile audit is
probably to decide whether plugin-local `include` / `require` should be
constrained to a plugin root or declared plugin dependency roots rather than
inheriting the standalone VM's ambient `cwd` / `MICROMAX_PATH` search convention.
