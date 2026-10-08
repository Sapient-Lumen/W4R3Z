# Research notes — rev0967

A bounded page is not a bounded algorithm when every candidate triggers another whole-model scan. The corrected projection first establishes one deterministic borrowed ordering, then groups each path once. This makes the expensive path classification shared rather than repeated and gives pagination one stable total order.

Visible-head selection can be expressed as causal coverage. For a path group, the maximum observed counter for each actor across candidate contexts is sufficient to decide whether another candidate supersedes a given operation dot. That replaces pairwise candidate comparison with one aggregation pass followed by one dot test per operation. The differential regression keeps the public pairwise predicate as an oracle rather than trusting the optimization by inspection.

Cursor validity is part of authority, not a convenience. The continuation token names an exact active superseded operation in the selected scope; accepting a stale, visible, malformed, or foreign-path token would silently change the meaning of the next page. Separate pages also cannot be treated as one atomic listing unless their replica and payload cutpoint digests agree.

Metadata-only historical reconciliation remains unsafe without an explicit crash protocol. An operation identifier is a deterministic browsing key, not necessarily a causally safe transfer order. Durable staging, payload obligations, or a causal ordering rule must exist before a remote predecessor may arrive without bytes.

The next product edge remains a deliberate history lifecycle: current/version/in-flight reachability, owner-visible bytes/count/age policy, crash-safe mark and quarantine, revalidation before unlink, friendly ordering metadata, conflict copies, and restore UX measured against one named Resilio uninstall workflow.
