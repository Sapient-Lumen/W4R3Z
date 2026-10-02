# ADR 0288: add read-only synchronization source preflight

Status: accepted 2026-09-01.

## Context

IoTox can create one-writer content/treepack namespaces and read-write tree-v2 namespaces, but the
first ordinary command crossed directly from an operator's path to namespace creation. Refusal of an
unsupported filesystem shape or quota overflow was correct but late, and operators had no bounded
inventory or staging estimate before granting authority. The precious-data graduation plan names
that visibility as its first engineering gate.

Preflight must not grow a parallel approximation of the synchronization rules, create the very state
it is supposed to inspect, or imply that source filesystem capacity proves managed-store capacity.

## Decision

Add owner-local `iotox sync-doctor PATH ...`. It shares the exact `sync-create` access/interval/
projection grammar. Regular one-writer sources use content-v2 scale estimation and the production
race-detecting digest path. One-writer directories reproduce the frozen treepack-v1 entry and artifact
accounting while hashing every file. Read-write directories invoke the production tree-v2 worktree
scanner and canonical manifest encoder directly.

The command accepts only normalized absolute non-root paths, follows no final symlink, writes no
state, and does not connect to the Agent. Its versioned line record hex-encodes the resolved path and
reports the policy, transformations, population, bytes, conservative first-revision store/staging
minima (including treepack's quota-charged canonical sort bound), object estimate, and default bounds.
It labels source-filesystem availability precisely and
always reports managed storage headroom and backup assessment as `not-probed`/`not-assessed`.

## Consequences

An owner can reject unsupported or oversized sources before namespace creation and can review the
semantic transformations read-write synchronization would make. The direct scanner reuse keeps new
tree-v2 behavior visible to the doctor automatically. Treepack accounting remains a small format-
bound implementation because publication produces a single packed artifact rather than a worktree
manifest.

This closes the source-inventory half of the preflight gate. It does not inspect a configured Agent
store, nondefault deployed quotas, current store pressure, convergence health, backup independence,
or restore success. Those limitations remain explicit until deployable configuration and namespace
health work land.
