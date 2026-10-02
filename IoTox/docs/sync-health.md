# Synchronization namespace health

Status: ADR 0297 implements the first durable health grammar for the read-write `tree-v2` engine.

`sync-status` is live process telemetry and `sync-repair` is an operator-requested integrity walk.
Neither answers, after a restart, what the last complete health inspection actually established.
`sync-health` performs that inspection and commits a fixed, content-free, stable-device-signed record:

```text
iotox sync-health shared-notes
iotox sync-health shared-notes cached
iotox sync-health shared-notes refresh
```

Refresh is the default. It verifies the current signed branch frontier and maintenance/cutoff state,
counts conflicts, hashes every selected file object, compares the signed workspace with the current
merge, checks the writable tree for uncommitted changes, samples automation failure streaks and the
last in-memory source set, accounts the active selected graph against the namespace store ceiling,
then atomically replaces `<namespace-root>/health.state`. `cached` verifies and reads that record
without walking content. A changed namespace policy makes the old record visibly
`policy-current=0`; the next refresh advances its sequence under the new policy commitment.

The single result line begins `iotox-sync-health-v1` and includes:

- `level=green|yellow|red`, derived from closed fields rather than supplied by a caller;
- complete versus partial custody intent, with exact desired/verified/missing object and byte counts;
- frontier/member/cutoff/conflict counts without keys or paths;
- stable/current/clean workspace facts;
- healthy/stalled/manual automation and its consecutive failure high-water;
- accounted active-store bytes and the configured ceiling;
- last observed exact-probe source count and absence/unavailability totals; and
- the permanent qualifiers `signed=1 rollback-witness=0 backup-certified=0`.

Green means the current selected closure is locally verified, the authenticated workspace matches
the current conflict-free merge, its worktree has no uncommitted edit, and no stall or pressure flag
is active. Expected sparse custody may therefore be green while still saying `custody=partial`.
Yellow means attention is required—for example a conflict, unprojected frontier, local edit,
automation failure streak of at least three, or at least 80% accounted store use. Red means selected
objects are missing, an exchange is pending, a required authenticated local layer is absent, or the
last observed bounded source set was exhausted. Structural/signature failures return an error rather
than producing a reassuring colored record.

## Deliberate limits

The record is a local observation, not remote attestation. Its signature detects modification but
cannot prove that an older valid health record was not restored. ADR 0314 witnesses tree-v2's live
branch frontier and exact signed workspace/maintenance state, not
`<namespace-root>/health.state`; its permanent `rollback-witness=0` therefore remains honest. The store
accounting covers the authenticated active frontier plus selected content; it is not a raw
filesystem-usage meter. Source evidence survives only when captured by a refresh and does not prove
that a source remains online. `content-v2`, `treepack-v1`, and `range-v1` retain their existing
repair/status surfaces; this first health command refuses them rather than inventing weak parity.

Most importantly, green does not certify a backup. It does not establish independent failure
domains, retention depth, deleted-history recovery, restore rehearsal, media health, or another
machine holding the complete closure. Those remain gates in `sync-trust-graduation.md`.
