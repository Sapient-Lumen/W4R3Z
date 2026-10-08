# Research — session readiness evidence and operator diagnostics

Current Linux service/session guidance suggests a clear product lesson for VHK.

## What current tooling/docs are teaching

- `ExecCondition=` is useful because it can skip the rest of startup without
  marking the unit failed when the session is not ready.
- `systemctl show` exists to expose structured unit properties directly instead
  of forcing maintainers to parse `status` output.
- `graphical-session.target` defines one specific session-lifetime boundary, but
  target binding alone does not explain why a start was skipped.
- `loginctl` and nearby session facts are still useful context, yet they are not
  substitutes for the readiness probe that the installed lane actually used.

## Product lesson for VHK

A Linux-native AHK-like system should preserve the evidence that links session
truth to operator triage. That means rehearsal and dossier lanes should carry a
compact readiness verdict, the underlying probe output, and nearby structured
unit properties together, so support can distinguish wrong-session skips from
ordinary daemon failures without re-running the machine from memory.
