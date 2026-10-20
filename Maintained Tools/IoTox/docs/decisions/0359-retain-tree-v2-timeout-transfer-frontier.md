# ADR 0359: Retain tree-v2 timeout transfer frontier

- Status: accepted and implemented
- Date: 2026-09-09

## Context

The first post-ADR-0358 cap-8 Sandwurm repeat rejected after the 1,800 second guest timeout. The
existing rejected receipt preserved partial worktree/store shape, but not the in-progress pull
frontier. It could say that both followers had only 194 capacity files, but not whether retained
tree-v2 jobs were awaiting inventory, awaiting objects, holding active lanes, committing batches, or
seeing source offer/unavailable counters.

That is insufficient for the next near-ceiling bottleneck. The current problem is no longer “did the
run converge?”; it is “where was object transfer/catch-up stuck when the accepted proof was not
reached?”

## Decision

Rejected three-writer receipts now optionally include
`partial_tree_v2_pull_summary_per_node`, a three-entry content-free summary parsed from each node's
`sync-status` before shutdown when possible.

Each node summary includes only aggregate counts:

- retained job state counts;
- selected/manifest/skipped object and path counters;
- availability request/result counters;
- active/staged lane counts and lane byte totals;
- requested/committed/reused/fetched object counters;
- accepted branch/conflict counters;
- file-commit batch and CAS inventory counters; and
- source aggregate requested/offered/absent/unavailable/committed/fetched counters.

If `sync-status` is unavailable during failure cleanup, the runner writes a zeroed summary for that
node rather than losing the rejected receipt.

## Consequences

Future rejected near-ceiling proofs can separate these cases without exposing content:

- no active job was present;
- jobs were waiting for inventory;
- jobs had active object lanes but were not committing;
- transport was offering objects but local admission/commit was stuck;
- CAS inventories were still amplifying commit work; or
- sources were returning absence/unavailability.

The verifier keeps old rejected proofs valid when the new field is absent. When present, it requires
three complete dictionaries of nonnegative integers and basic internal bounds such as active/admitted
lanes not exceeding lane records.

This is evidence plumbing only. It does not change sync protocol behavior, signed records, local
authority, or convergence semantics.

## Evidence

Accepted local checks:

```text
python3 -m py_compile tools/run-sync-three-writer.py tools/verify-sync-three-writer-sandwurm.py tools/export-sync-three-writer-sandwurm.py
python3 tools/verify-sync-three-writer-sandwurm.py --self-test
python3 tools/export-sync-three-writer-sandwurm.py --self-test
```
