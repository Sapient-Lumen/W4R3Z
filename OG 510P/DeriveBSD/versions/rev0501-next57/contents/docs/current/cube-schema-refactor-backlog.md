# Current cube schema refactor backlog

The live schema-refactor backlog is `cube.schema.refactor.backlog` for 2026-05-30r533. It is generated from the schema audit and turns const-heavy/runtime-contract debt into an ordered work queue.

Current backlog counts:

```text
items_total: 21
open_items: 11
completed_items: 10
post_detach_items: 17
highest_const_count: 201
audit_next_targets_count: 7
```

r533 closes the successor-index cutover split item and selects the next post-detach const-heavy schemas from the live audit. The next cuts should continue with the next open p0 post-detach schema unless a more urgent runtime correctness seam appears.

Last updated: 2026-05-30r533

Refactor pattern token: `generic-runtime-schema-plus-exact-fixture-schema`.
