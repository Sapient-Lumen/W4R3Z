# Cooperation benchmark programs should publish direct role-annotated focus primary verify and refresh targets for compact-card reentry

## Claim
A compact-card reentry surface should publish one direct role-annotated `focus_primary_verify_target` and one direct role-annotated `focus_primary_refresh_target` witness alongside the first focus commands.

## Why
A direct command witness answers what to run, but it still leaves the inheritor to infer what that command is for. Direct role-annotated focus command targets keep the global reentry surface locally self-explanatory while reusing retained pack/report paths.

## Minimal contract
- `focus_primary_verify_target` and `focus_primary_refresh_target` should agree with the chosen focus lineage handoff pack when one exists.
- The targets should be compact aliases of retained report paths, not new generated summaries.
- `role_codes` should make the command intent legible without requiring script-name archaeology.
