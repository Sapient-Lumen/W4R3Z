# Cooperation benchmark programs should publish direct selected-command-ladder required-lane fields for compact-card next-action surfaces

If a compact-card next-action surface publishes a multi-step selected command ladder, each rung should also publish the execution lane it requires and whether that lane is currently available.

Concretely, the witness should publish `selected_command_ladder[].required_lane_id` and `selected_command_ladder[].required_lane_available`, and the primary next-action surface should mirror the same rung objects onto `primary_action.command_ladder`.

This keeps fallback and reentry guidance environment-honest at each step instead of forcing inheritors to assume one top-level lane requirement applies uniformly to the whole ladder.
