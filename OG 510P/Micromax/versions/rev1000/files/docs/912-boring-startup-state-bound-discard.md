# Rev0954 — boring startup and state-bound discard confirmation

Micromax's trust promise is not satisfied because a command *usually* warns.
The warning must describe the state that a later destructive action will
actually discard, and every front end must start from a renderable editor even
when the requested first file fails.

Rev0954 fixes three related ways the product could bypass that promise:

1. the CLI and TUI had separate initial-buffer logic, and a failed directory
   open could leave the headless renderer with zero buffers;
2. the headless REPL handled `:q` and EOF by leaving its loop directly instead
   of using the editor's dirty-buffer policy;
3. `quit`, `close`, `closeall`, and `only` remembered confirmation with mutable
   booleans, so warning → edit again → repeat could discard text that had never
   been confirmed.

The landing also adds complete trusted and restricted startup/edit journeys and
makes these boundaries visible in `tools/mxaudit.py` as their own editor-trust
section rather than hiding them among plugin-lifecycle checks.

## Product invariant

After shared startup returns, the editor has one live active buffer. If a
requested path or help document could not open, the caller receives a typed
failure result and a visible diagnostic, while the editor falls back to a live
buffer—normally `*scratch*`.

A non-forced destructive command succeeds only when either:

- no dirty buffer would be discarded; or
- the immediately retained confirmation witness still matches the exact
  operation scope.

A warning is not a transferable permission bit. Any relevant change replaces
it with a new witness and requires one more explicit attempt.

## Shared initial-buffer boundary

`src/micromax_editor/startup.py` now owns `open_initial_buffer()` and
`InitialBufferResult`.

The result records:

```text
ok              whether the requested target opened
kind            scratch, path, or help
requested       the original target text
active          the guaranteed live active buffer
fallback_used   whether startup had to recover
message         the stable visible recovery diagnostic
```

`_ensure_active_buffer()` chooses, in order:

1. the already-valid active buffer;
2. a live MRU buffer;
3. the last live buffer;
4. a new `*scratch*` buffer.

Both the CLI and curses TUI use this owner. A failed `--dump-screen` request now
prints valid screen-model JSON for the fallback buffer and exits nonzero instead
of raising `RuntimeError: No active buffer`. Interactive startup may continue in
the fallback and keeps the diagnostic in editor messages.

The boundary catches ordinary open exceptions, but it does not catch
`BaseException` classes such as process exit or keyboard interruption.

## State-bound discard witness

`src/micromax_editor/discard_guard.py` is a small side-effect-free owner. The
editor holds one `DiscardConfirmationGuard`, replacing four independently
mutable flags.

Each discarded buffer witness captures:

- visible buffer name;
- live `EditorBuffer` object identity through a weak reference;
- monotonic `Buffer.version`;
- dirty bit;
- path.

The weak reference avoids retaining a potentially large closed buffer while
still preventing Python object-id reuse or same-name replacement from being
accepted as the warned target. Version deliberately invalidates confirmation
even when an edit is undone back to identical text: the user changed state after
the warning, so the safe and predictable response is to show the warning again.

Operation scopes are explicit:

| Operation | Captured discard scope | Retained context |
| --- | --- | --- |
| `quit` | all live buffers | none |
| `close [NAME]` | the exact target buffer | none |
| `closeall` | all live buffers | none |
| `only` | every buffer except the current keep target | keep target name and live identity |

The `only` anchor matters because replacing the kept object under the same name
must not turn an old warning into consent for a new operation context. Edits to
the kept buffer do not re-arm because that buffer is not discarded; replacing
its identity does.

`request()` has three outcomes:

- `armed` — first warning;
- `rearmed` — some prior witness existed, but operation, target set, identity,
  version, dirty state, path, or retained context changed;
- `confirmed` — an exact second request; the guard clears before success.

Changing to another command family or running an unrelated command clears the
pending witness. Force forms (`quit!`, `close!`, `closeall!`, `only!`, or the
existing force flags) remain explicit one-shot choices.

Read-only `_quit_armed`, `_close_armed`, `_close_armed_name`,
`_closeall_armed`, and `_only_armed` properties remain temporarily as
compatibility views for prompt previews and downstream probes. There are no
mutable setters.

## Shared warning language

The four command paths now use `format_discard_warning()` rather than carrying
near-duplicate preview/count formatting in the 29k-line coordinator and command
modules.

The first request names the unsaved buffers and exact repeat/force choices. A
changed witness says that the discard scope or unsaved state changed, names the
currently unsaved buffers, and says confirmation was refreshed. It does not
pretend every refresh came from a text edit: opening, replacing, renaming, or
changing the retained `only` context can also invalidate the evidence.

## Headless exit semantics

`run_headless_repl()` is now an independently testable front-end loop.

- `:q` executes normal `quit` and therefore needs an unchanged second request
  when dirty buffers remain.
- `:q!` executes explicit forced quit.
- EOF executes normal `quit`; it is never treated as the second confirmation.
- On a terminal, dirty EOF reports the refusal, clears the witness, and returns
  to the prompt so a user can choose `:q` or `:q!`.
- On exhausted non-interactive input, dirty EOF reports the refusal and returns
  status 2 instead of claiming a clean status-0 shutdown.
- Clean/autosaved EOF exits normally.

The active cursor is remembered through one `finally` path rather than three
ad hoc exit branches.

## Journey evidence

`tests/test_editor_startup_discard_trust.py` exercises:

- no-target scratch startup;
- directory and unexpected open failures with a live fallback;
- failed `--dump-screen` producing valid JSON plus a nonzero status;
- edit-after-warning re-arm for all four destructive families;
- buffer-set, explicit-target, keep-target, and same-name identity changes;
- prompt previews dropping stale armed state;
- safe and forced REPL quit;
- terminal and non-interactive EOF behavior;
- a trusted open → edit → undo → redo → save → external conflict → diff →
  forced recovery save → state-bound close journey;
- restricted startup scanning but not loading plugins/user init while host-owned
  save defaults remain usable.

Existing quit/close/prompt/CLI tests remain compatibility anchors. The structural
audit additionally rejects restoration of mutable armed assignments, split
initial-buffer ownership, direct REPL quit bypass, or removal of the journey
regressions.

## Audit/refactor judgment

This is a useful coordinator extraction because it has one owner, one invariant,
and adversarial evidence. It removes state from `Editor` rather than wrapping a
second editor around it.

The audit also found a separate trust-shaped seam that is not changed here:
`Editor.new_buffer(name, ...)` still overwrites an existing mapping entry with
the same name. Current product open paths usually avoid collisions and the
method is not yet a public Micromax hostcall, but future buffer-creation UI must
not inherit silent replacement. A later bounded change should distinguish
collision-free creation from an explicit, guarded replacement operation and pin
help/scratch naming behavior before exposing it.

## Residual limits

- The witness trusts the `Buffer.version` mutation invariant. Code that mutates
  buffer internals without using supported edit paths can violate more than this
  confirmation contract and remains unsupported.
- This protects in-memory discard decisions, not hostile process compromise,
  memory exhaustion, or arbitrary native/Python extensions.
- A fallback scratch makes startup usable; it does not make the requested open a
  success. Machine callers must inspect the result or process status.
- The curses front end keeps running after a failed initial target because it is
  interactive; it surfaces the message rather than returning the headless dump
  status.
- Focused and timely checks are bounded health evidence, not a complete current
  full-suite release claim.

## Next cuts

1. Migrate the remaining legacy fork-first filesystem workers while preserving
   deterministic test doubles and platform behavior.
2. Audit buffer-name collision semantics before adding a public new-buffer
   command or hostcall.
3. Pin replace cancellation, recovery/restart persistence, and save-failure
   journeys with the same visible-state discipline.
4. Define one restrained screen-model highlight hierarchy before building a
   broad theme engine.
5. Use real project editing to choose the next bounded flow primitive rather
   than defaulting to a background index.
