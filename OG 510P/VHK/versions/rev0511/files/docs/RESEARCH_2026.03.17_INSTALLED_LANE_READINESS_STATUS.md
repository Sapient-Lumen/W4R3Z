# Research — installed-lane readiness status

Current Linux service/session tooling suggests a clear next lesson for VHK.

## What current tooling/docs are teaching

- `ExecCondition=` is valuable because a service can be skipped for a reviewed
  reason without being treated like a normal crash.
- `systemctl show` is the structured unit-state lane, and recent docs keep
  emphasizing that properties such as `ActiveState`, `SubState`, `Result`, and
  `ConditionResult` are better machine inputs than scraping formatted status
  output.
- `loginctl show-session` is explicitly the computer-parsable session lane, so
  Linux operator tooling should keep lightweight session facts accessible
  without forcing a full debug bundle every time.
- `graphical-session.target` remains one specific lifetime boundary, but it does
  not by itself explain whether the installed lane looked ready when the user
  asked.

## Product lesson for VHK

A Linux-native AHK-like system should keep two operator proof scales:

1. a lightweight installed status bridge for everyday support/questions
2. a heavier rehearsal/dossier lane for full packet capture

The first should already be able to say `ready`, `not_ready`, `unavailable`, or
`error` from the installed lane itself, while the second keeps the richer
support evidence when the issue needs escalation.
