# Scenario: release drift changes declared and effective boundary

A later release adds `public = true` for one dependency, removes another from the visible API, and resolves a workspace gap.
The diff must classify each kind of change separately.
