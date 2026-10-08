# REV0306 — session readiness evidence in rehearsal and dossier

This revision takes the session-readiness contract from rev0305 and threads it
into the operator-facing proof lanes.

## What changed

- Added `src/vhk/project/session_readiness_evidence.py`
- `gen-host-rehearsal-pack` now emits session-readiness evidence in story/summary/docs
- Host rehearsal reports now capture:
  - the installed `verify_session_readiness.sh` output
  - its exit code
  - a matching `systemctl --user show` property slice for the owned unit lane
- `gen-host-dossier-pack` now captures the same readiness evidence directly
  into the support packet
- Rehearsal and dossier Markdown/JSON output now classify readiness as
  `ready`, `not_ready`, `error`, or `unavailable`

## Why it matters

Linux-native automation needs more than install truth and service ownership. It
also needs evidence that explains when a lane was skipped because the session
was not ready yet. This revision makes that evidence portable and reviewable.
