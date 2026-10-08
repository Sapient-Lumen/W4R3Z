# REV0303 — graphical-session lifetime binding and session-target probes

This revision extends the Linux-native service handoff again by making
**graphical-session lifetime** explicit instead of leaving it implicit behind
activation sync and generic user-service wording.

## What changed

- Added `src/vhk/project/session_target_policy.py`
- `gen-service-compose-pack` now emits `session_target_policy` in plan JSON
- Generated service handoffs now include:
  - `docs/VHK_SESSION_TARGETS.md`
  - `verify_session_targets.sh`
- Generated VHK-owned user units now declare `BindsTo=graphical-session.target`
  when the lane is graphical-session-bound
- Install/uninstall helpers now carry the session-target probe script and clean
  up explicit `graphical-session.target.wants/` links created during install

## Why it matters

Linux session startup is not only an environment problem. Session-specific
automation often needs three separate truths to stay visible at once:

- who owns authority
- which live variables must be imported into activation environments
- whether the VHK-owned unit should follow graphical-session lifetime

This revision makes the third truth reviewable in code, docs, and shipped
artifacts.
