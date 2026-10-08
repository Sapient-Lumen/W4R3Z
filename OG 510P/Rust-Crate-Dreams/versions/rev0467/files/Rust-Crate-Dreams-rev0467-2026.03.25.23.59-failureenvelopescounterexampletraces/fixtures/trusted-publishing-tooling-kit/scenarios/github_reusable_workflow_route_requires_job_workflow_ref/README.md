# GitHub reusable workflow route requires `job_workflow_ref`

This scenario captures the case where a repository uses a reusable workflow for release.
The caller workflow file is not the whole route: the OIDC token can expose `job_workflow_ref`, and that route fact should stay visible in the claim-basis receipt.
