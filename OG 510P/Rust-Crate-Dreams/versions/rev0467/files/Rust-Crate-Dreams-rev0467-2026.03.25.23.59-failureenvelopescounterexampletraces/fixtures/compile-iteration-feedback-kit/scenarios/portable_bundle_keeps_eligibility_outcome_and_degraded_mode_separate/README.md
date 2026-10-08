# Scenario — portable bundle keeps eligibility, outcome, and degraded mode separate

This scenario proves the bundle-level inventory rule for the current compile-iteration lane.

A patch-eligible edit can still fail to apply.
A successful activation boundary can still coexist with degraded live-update mode.
A restart fallback plan can exist even when the current session is still running.
The bundle should therefore keep those truths separate instead of collapsing them into “reload worked”.
