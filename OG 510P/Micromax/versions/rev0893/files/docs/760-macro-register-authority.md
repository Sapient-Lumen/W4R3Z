# Rev0802 — macro register authority

Rev0802 continues after the rev0800 interaction rollback and rev0801 savecursor authority landings, moving the protected-register audit on saved macros.  Recent revisions had already protected undo/redo, clipboard, prompt history, recent rows, message/help history, selection stacks, jumplists, and named-mark mutation.  Saved macros needed the same treatment because they are not just metadata: they are delayed executable editor state.

## Failure mode

Before this revision, mutation of macro slots was guarded, but read/replay access was still too broad.  A lower-authority script could ask for the portable payload of a trusted/user macro through `ed.macro-get`, inventory trusted macro names/counts through the macro row helpers, or trigger a trusted macro slot through script-origin `ed.macro-play` / scripted `macro play`.

The direct replay path still ran under script context, so it did not grant raw `cap.*` mutation power.  But it could still consume user-authored recovery/executable state and expose saved command payloads that may contain file names, commands, search terms, or other private workflow evidence.  That made macros inconsistent with the protected-register model used elsewhere in the editor.

## Change

`src/micromax_editor/macro_policy.py` now has a read/replay access policy beside the existing mutation policy:

- trusted interactive/user callers keep normal access;
- a script can read and replay macro slots it created itself;
- same-plugin callbacks can access slots from the same loaded plugin generation;
- trusted/user macro slots and other-origin script/plugin slots are denied by default;
- `cap.macro-read` is the explicit override for inspection;
- `cap.macro-play` is the explicit override for replay.

`Editor.get_macro(...)`, `macro_names()`, `macro_inventory_rows()`, `macro_status_rows()`, and `macro_detail_row(...)` now respect the read boundary.  `Editor.play_macro(...)` now preflights replay authority before executing the first step.  Denied replay reports a visible `macro play:` message and leaves the buffer unchanged.

The bridge was also tightened around the adjacent macro hostcalls.  `ed.macro-get`, `ed.macro-detail-row`, and `ed.macro-record` now peek and preflight their string argument before consuming it.  A denied `ed.macro-get` leaves the macro name on the VM stack for diagnosis rather than eating the evidence.

## Capabilities

New unsafe capabilities:

- `ed.macro-read` / `cap.macro-read`: allow scripts to inspect trusted or other-origin saved macro payloads and inventory rows.
- `ed.macro-play` / `cap.macro-play`: allow scripts to trigger replay of trusted or other-origin saved macro slots.

`cap.macro-play` is intentionally not a trust upgrade.  When a script is allowed to trigger a protected macro slot, the macro steps still run under script authority, so `cap.*` self-escalation and host-operation gates remain active.

## Validation

Focused regressions cover denied script replay of trusted macros, same-origin script macro replay, explicit `cap.macro-play`, denied script inspection of trusted macro payloads, VM-stack preservation for denied `ed.macro-get`, explicit `cap.macro-read`, and cross-script macro isolation.

The existing macro named-hostcall roundtrip was updated to acknowledge the new rule: a trusted host-created macro slot needs explicit `cap.macro-play` when replayed through the script-origin `ed.macro-play` hostcall.

## Remaining risk

This is still an editor-level provenance model, not a process sandbox.  Trusted interactive code can inspect and replay all macros by design.  Future macro persistence, import/export, or UI surfaces should reuse `macro_access_policy(...)` rather than walking `self.macros` directly.  Named marks now have mutation provenance but still expose some read/navigation surfaces; that is a plausible next protected-register audit lane.
