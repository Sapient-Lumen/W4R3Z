# Scenario — hot-lib-reloader signature or tracing issues demand restart or disable-live-update posture

This scenario proves why a compile-iteration bundle must describe the **observed outcome** and **current mode**, not just the nominal route.

`hot-lib-reloader` documents signature changes as likely crash-inducing, type/layout changes as undefined-behavior risks, and known `tracing` combinations as crash or corruption hazards.
In those conditions, the honest posture is often `restart_required` or `disabled_due_to_error`, not “hot reload probably still works”.
