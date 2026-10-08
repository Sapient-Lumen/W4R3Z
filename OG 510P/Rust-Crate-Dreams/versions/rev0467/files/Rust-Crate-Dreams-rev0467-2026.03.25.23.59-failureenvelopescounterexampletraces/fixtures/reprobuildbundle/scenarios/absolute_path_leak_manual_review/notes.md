# Scenario — absolute path leak remains after rebuild

Two builds use the same source and lockfile, but the rebuild omitted path-sanitization settings.
The result is a material mismatch in debug information and panic-site strings.

This scenario is intentionally **not** classified as semantic reproduction.
The likely next action is to align path-remapping / trim-paths policy and rebuild.
