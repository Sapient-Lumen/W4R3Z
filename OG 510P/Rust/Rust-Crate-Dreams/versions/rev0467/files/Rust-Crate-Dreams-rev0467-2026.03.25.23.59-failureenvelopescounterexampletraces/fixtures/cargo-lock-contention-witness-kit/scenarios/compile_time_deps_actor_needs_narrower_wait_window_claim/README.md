# Scenario: compile-time-deps actor needs a narrower wait-window claim

A tool-facing lane uses `--compile-time-deps`.
The bundle must not overclaim that the whole workspace build lane was blocked when only the compile-time lane was directly observed.
