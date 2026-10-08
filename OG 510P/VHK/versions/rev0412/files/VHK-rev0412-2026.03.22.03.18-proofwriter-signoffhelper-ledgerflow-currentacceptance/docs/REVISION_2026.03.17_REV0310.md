# REV0310 — installed-lane startup handoff drift

This revision adds a bounded startup-owner history to the installed status bridge.
Native-install output now preserves one `startup_handoff_drift` verdict alongside
current startup ownership, and support/rehearsal/dossier surfaces now render that
longer-lived startup-owner truth.
