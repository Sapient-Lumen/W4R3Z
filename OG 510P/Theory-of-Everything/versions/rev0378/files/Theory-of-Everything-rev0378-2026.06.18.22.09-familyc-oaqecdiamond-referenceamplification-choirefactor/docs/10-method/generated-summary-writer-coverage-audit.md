# Generated-summary writer coverage audit

This audit checks that every registered route-support family with a `generated_summary` path is also referenced inside `tools/sync_generated_surfaces.py`.

It closes a restart failure mode: a family can have ledgers, schemas, route fields, and a summary path in the registry, but if the writer is not wired into `make index`, the summary becomes stale while the rest of the cube appears current.
