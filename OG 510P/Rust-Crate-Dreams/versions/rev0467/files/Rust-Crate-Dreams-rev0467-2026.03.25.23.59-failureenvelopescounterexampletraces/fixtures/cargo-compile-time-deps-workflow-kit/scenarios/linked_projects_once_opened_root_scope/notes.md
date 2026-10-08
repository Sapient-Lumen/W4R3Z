# linked_projects_once_opened_root_scope

This scenario exists to keep the crate honest about linked-project topology.

If there are multiple linked projects and override commands run with `once`, the opened project root is not the same claim as a per-workspace sweep.
The bundle should freeze that narrower root and avoid silently implying per-workspace coverage.
