# ADR 0294: Add a forward-only synchronization time machine

- Status: accepted and implemented
- Date: 2026-09-02

## Context

Tree-v2 already retained signed branch records, conflict provenance, checkpoint floors, explicit
pins, recoverable quarantine, and writer cutoffs. Operators could protect a record but could not list
retained revisions, compare two records, inspect conflicts directly, or safely select old content.
Reusing `sync-restore` or changing a current branch pointer to an old signed record would confuse GC
repair with content recovery and violate the forward-only branch contract.

## Decision

Add `sync-history`, `sync-diff`, `sync-conflicts`, `sync-restore-plan`, and
`sync-restore-forward`. Advance owner-local control to v1.52 operations 115--119; peer tree-v2 and
Ratox frames remain unchanged.

History inventories and cryptographically reloads every live retained immutable branch record,
marks current/checkpoint/pin facts independently, and orders the bounded result per writer rather
than claiming a global clock. Diff compares exact canonical candidate sets and separately marks
projected content changes. Conflict output exposes bounded path/provenance metadata but no content.
Paths are hexadecimal and every response has an explicit omission count beneath the 60 KiB local
control ceiling.

A restore plan is an optimistic-concurrency commitment over the canonical namespace policy,
authenticated maintenance record or its established absence, exact current branch frontier, current
merged manifest, stable signed workspace record, clean scanned worktree, target record/manifest, and
required object identities/sizes. Planning writes nothing. A target with conflicts or missing
objects, a dirty/stale workspace, an already-current target, or a revision exceeding current quota is
not ready.

Apply re-derives and constant-time checks the exact plan. It creates one conflict-free manifest whose
selected target paths and necessary tombstones are all authored by the local writer at its next
generation, with the exact visible frontier as causal history. Immutable manifest and signed branch
commit before ordinary journaled worktree reconciliation. No operation writes the target record into
a current pointer or decrements a generation.

Keep `sync-restore` exclusively for recoverable GC quarantine. Historical recovery requires the
visibly distinct `sync-restore-forward ... PLAN_ID` ceremony. Do not add `sync-rollback`.

## Consequences

Operators can now understand and recover a recent retained tree without filesystem surgery, and the
recovery itself replicates as a normal authorized revision. A stale plan cannot cross concurrent
local edits, remote convergence, policy/cutoff/pin changes, or its own successful replay. Target
conflicts require a separate explicit resolution rather than deterministic-but-silent loss.

This history is bounded by retention and storage quotas and shares the host, device key, and rollback
domain with current state. It cannot recover a lost host, prove freshness after whole-state replay,
or replace an independent backup. Workstream 8 owns an independent rollback witness; backup trust
still requires separately recoverable copies under `sync-trust-graduation.md`.

Two new direct tests bring the owned registry to 740. One proves inventory/pin/diff/conflict/plan,
dirty-worktree refusal, stale-plan refusal, forward generation/previous linkage, restored bytes, and
replay refusal. The other proves exact missing-object accounting. The live Agent integration repeats
checkpoint, history, diff, conflict, plan, and forward restore through local control and the real
writable automation worktree.
