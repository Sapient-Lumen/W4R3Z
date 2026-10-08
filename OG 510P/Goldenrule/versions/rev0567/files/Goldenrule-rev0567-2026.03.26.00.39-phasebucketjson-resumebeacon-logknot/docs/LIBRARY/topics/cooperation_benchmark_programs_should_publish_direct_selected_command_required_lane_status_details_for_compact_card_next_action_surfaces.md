# cooperation benchmark programs should publish direct selected command required lane status details for compact-card next-action surfaces

When a compact-card next-action surface publishes a selected command or a selected command ladder, it should also publish the required lane's local status details instead of forcing inheritors to reopen the full execution-lanes report.

Concretely, the ladder witness should publish `selected_command_ladder[].required_lane_summary` and `selected_command_ladder[].required_lane_blocking_reason_codes`, and the primary next-action surface should mirror those rung fields while also publishing `primary_action.required_lane_summary` and `primary_action.required_lane_blocking_reason_codes`.

This keeps the reentry ladder environment-honest in-place: an inheritor can see not only whether a step is runnable, but which lane semantics apply and which blocking reasons are present if that lane is unavailable.
