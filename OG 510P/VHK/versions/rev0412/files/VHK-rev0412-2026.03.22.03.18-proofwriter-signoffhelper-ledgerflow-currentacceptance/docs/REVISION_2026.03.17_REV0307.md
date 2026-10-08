# REV0307 — installed-lane readiness status bridge

This revision takes the session-readiness truth from service/rehearsal/dossier
lanes and threads it into the lighter-weight installed/operator surfaces.

## What changed

- Added `src/vhk/project/session_readiness_status.py`
- Refactored host rehearsal/dossier readiness verdict parsing to use the shared helper
- The native installed launcher status/report path now captures:
  - one installed readiness probe verdict
  - nearby user-unit `Result`/`ConditionResult` facts
  - a compact human summary in status Markdown
- `gen-support-pack` now emits an installed-lane status bridge in:
  - `docs/VHK_SUPPORT_GUIDE.md`
  - `docs/VHK_SUPPORT_CHECKLIST.md`
  - `docs/VHK_SUPPORT_PLAN.json`
  - `scripts/vhk_capture_support.sh`

## Why it matters

Linux-native automation does not always need a full dossier packet just to say
“the session was not ready.” This revision gives VHK one lighter operator lane
that can expose that truth directly from the installed launcher before support
has to escalate to heavier capture flows.
