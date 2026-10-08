# Scenario — reusable workflow release needs a route receipt, not just the caller filename

A GitHub release flow delegates publishing to a reusable workflow.
The trusted-publishing lane should record both the caller route and the `job_workflow_ref`-style called route so a reviewer can see what identity path was actually exercised.
