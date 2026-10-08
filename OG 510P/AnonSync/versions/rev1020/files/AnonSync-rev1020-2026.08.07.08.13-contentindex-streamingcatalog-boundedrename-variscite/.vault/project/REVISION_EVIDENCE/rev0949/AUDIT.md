# Rev0949 audit summary

The audit found two composition/performance defects in the shipping C++ folder
path. First, one `maximum_entries` value counted all namespace objects while also
being constrained by regular-file catalog and payload capacities. Rev0949 adds
an independent `maximum_regular_files` contract and carries it through observer,
owner, service, CLI, provisioning, reports, and process tests. Second, a known-
large or tombstone-heavy catalog could attempt a complete speculative idle proof
before falling back to the bounded durable scan. The gate now executes before
replica projection and traversal. Exact stop reasons make the remaining bounded
behavior observable without changing deletion authority.

The principal remaining scale costs are per-directory full-name buffering,
root-prefix replay, whole-catalog completed-epoch adjudication, restart-cold
payload scans, and unbounded retained history. See
`NAMESPACE_FILE_CAPACITY_AND_IDLE_FRONTIER_AUDIT_rev0949.md`.
