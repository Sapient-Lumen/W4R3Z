# ADR 0357: Retain tree-v2 apply counters in Sandwurm receipts

- Status: accepted and implemented
- Date: 2026-09-09

## Context

ADRs 0354--0356 added content-free source, CAS, projection, conflict, and preservation counters to
normal tree-v2 publish and pull status. The near-ceiling Sandwurm receipts still retained only older
batch/inventory counters. That meant future runs could prove a wall-clock regression without keeping
the final local apply shape needed to explain it.

## Decision

Extend `tools/run-sync-three-writer.py` so `tree_file_batch_summary()` parses all
`reconcile-*` counters from retained `tree-job=` status rows for the tested namespace. Passed
capacity receipts now include:

```text
capacity_reconcile_apply_per_node=[{...}, {...}, {...}]
```

Each dictionary stores non-secret integer totals for source walk, source digest reuse, local CAS
inspection/install/reuse, selected projection copy volume, conflict material, and sparse
preservation. The verifier treats the field as optional for old proofs, but if present it requires
three complete dictionaries and at least one projected-file count in a capacity campaign.

## Consequences

Future near-ceiling proofs keep enough local-apply data to decide whether to attack projection,
source walks, CAS admission, or transfer scheduling next. Existing compact proofs remain valid
because the new receipt field is optional in the verifier.

No product protocol, authority rule, signed state, or Sandwurm launch contract changes.

## Evidence

Accepted local checks:

```text
python3 tools/verify-sync-three-writer-sandwurm.py --self-test
python3 tools/export-sync-three-writer-sandwurm.py --self-test
```
