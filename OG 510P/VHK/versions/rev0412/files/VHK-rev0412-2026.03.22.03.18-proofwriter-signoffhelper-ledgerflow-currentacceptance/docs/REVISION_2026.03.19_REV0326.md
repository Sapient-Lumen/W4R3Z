# Revision 0326 — i3/X11 runtime stack and session-bound simple busd units

This revision makes the **flagship warm-runtime lane** much easier to discover
and harder to misconfigure.

## What changed

- added `vhk gen-i3-busd-stack`
  - writes a socket-activated busd pair
  - writes a bus-emitting i3 snippet
  - writes a short install README
- changed `vhk gen-vhk-busd-service` to be **session-bound by default**
- changed `vhk gen-vhk-busd-socket-units` to be **session-bound by default**
- added docs for the i3/X11 runtime stack and updated `docs/BUS_DAEMON.md`

## Why this matters

The repo already had the pieces for the resident runtime, but they were spread
out across separate commands and richer pack generators. This revision makes the
main product lane more obvious:

- i3/X11 first
- thin `vhk-emit` trigger path
- warm resident runtime
- session-bound desktop lifetime
- preserved ad hoc CLI runs
- clearer control surface for a private LLM

## Validation

- focused CLI tests for busd service/socket generation pass
- new CLI test for `gen-i3-busd-stack` passes
- `python -m compileall -q src/vhk tests` passes
