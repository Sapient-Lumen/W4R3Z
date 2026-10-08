# 356 — `helpresume` active-case command honesty

`helpresume` exists to reopen the last **dormant** session-local docs target.

By rev413 the inspectable docs-navigation model already told the truth about that:

- `help_session_*` could still witness the current session-local docs head,
- `help_resume_available` only became true when that head was actually dormant and resolvable,
- `help_resume_command` stayed blank when the current help page was already active.

But one command-level seam still lingered underneath that same model: on an already-active help page, plain `helpresume` / `ed.help-resume` still succeeded and replayed the current page even though every inspectable surface said there was nothing off-screen to resume.

That was tiny, but it was still a trust break: the status/model surface and the command/hostcall surface no longer described the same actionability contract.

## Rule

If the current help/docs page is already active on-screen, `helpresume` is **not** actionable.

So the command/hostcall should fail plainly instead of replaying the current page:

- command: `helpresume: already active: topic @ line:col`
- hostcall: `ed.help-resume` returns `0`

## Why this belongs

This keeps Micromax aligned with the trust lesson repeated across the other datacubes:

- witnessed state is not automatically actionable,
- durable cues should only advertise real next actions,
- once a surface says an action is unavailable, the action path itself should fail closed instead of quietly doing something nearby.

## Scope

Deliberately tiny:

- no new state fields,
- no new commands,
- no history mutation changes,
- no persistence changes.

Only the active-case `helpresume` command/hostcall path changes so it matches the already-correct model.
