# Readonly hostcall edit boundary (rev777)

## Audit finding

The ordinary action path already refused mutating actions while the effective
`readonly` option was true, and the save path refused protected buffers.  The
lower-level Micromax hostcall surface was less consistent: `ed.set-text` had its
own one-off check, while `ed.replace-range`, `ed.delete-range`, and
`ed.replace-selections` edited the current buffer directly.

That mattered because these hostcalls are exactly the substrate used by scripts,
plugin helpers, deferred callbacks, and future UI adapters.  A protected help or
readonly user buffer could reject `InsertText` yet still be changed by a direct
VM call to `ed.replace-range`.

## Change

Rev777 adds:

`src/micromax_editor/edit_boundary.py`

The module owns the small shared policy:

- `buffer_is_protected(ed)` checks the active effective readonly/protected state
  and fails closed if the editor cannot answer;
- `readonly_edit_message(operation)` keeps denial wording stable;
- `require_editable_buffer(ed, operation, error_cls=...)` emits the same UI
  message witness and raises the caller's host-facing error.

`micromax_bridge` now routes these direct text-mutating hostcalls through the
shared guard before consuming operation arguments:

- `ed.set-text`
- `ed.replace-range`
- `ed.delete-range`
- `ed.replace-selections`

Keeping the guard before argument consumption means a failed readonly call leaves
its operation arguments on the stack for debugging, while the `hostcall` word has
already consumed the hostcall name as usual.

The existing `ed.insert` and `ed.backspace` hostcalls already delegate to
`run_action(...)`, so they keep using the action-level readonly policy.

## Why this was risky

This was not just a cosmetic gap.  The repo now has many authority-preserving
surfaces: script context, plugin callback roots, macro replay provenance, and
script dirty/autosave taint.  If a low-level edit primitive ignores readonly, all
of those surfaces inherit a surprising escape hatch.  The fix keeps the boundary
close to the low-level hostcall bridge, where future direct edit hostcalls can
reuse it.

## Validation

Focused regressions in `tests/test_editor_readonly_option.py` prove that direct
text-mutating hostcalls fail with `MicromaxError`, preserve their arguments on
failure, leave buffer text unchanged, and record visible readonly denial
messages.  The same test file also pins the delegated `ed.insert`/`ed.backspace`
behavior.

`tools/mxdoctor.py` now includes the readonly option test file in the bounded
handoff lane so this hostcall edit boundary stays in the default preflight.

## Remaining risk

This boundary protects editor-hosted VM hostcalls.  It does not make arbitrary
trusted Python plugin code transactional; a plugin with direct access to editor
objects can still mutate Python objects by design.  The next adjacent audit
should keep looking for newly added direct text-mutating hostcalls and route them
through the same seam.
