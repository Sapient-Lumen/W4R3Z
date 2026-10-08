# REV0312 — installed incident signatures

This revision adds installed-lane incident signatures so VHK can distinguish
clean session skips, generic condition skips, start-limit churn, real service
failures, missing units, and probe/runtime breakage on the installed status
surface.

## Main changes

- add `src/vhk/project/session_incident_signature.py`
- extend installed launcher status generation in `src/vhk/project/native_install_pack.py`
- extend support/rehearsal/dossier reporting to preserve incident-signature
  verdicts and summaries
- add focused tests for incident-signature classification and affected pack
  outputs
