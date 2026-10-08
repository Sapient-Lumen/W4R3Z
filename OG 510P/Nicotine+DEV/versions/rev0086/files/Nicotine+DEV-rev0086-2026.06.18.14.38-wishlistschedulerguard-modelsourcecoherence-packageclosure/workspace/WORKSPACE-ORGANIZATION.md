# Workspace organization for future passes

## Permanent cube content

The datacube should stay small and mostly textual:

- `docs/` — human-readable policy, worklogs, strict/backlog documents.
- `data/` — ranked queues, clusters, batch plans, extracted finding matrices.
- `sources/` — source references, commit IDs, hashes, metadata snapshots; no bulky source trees.
- `evidence/` — small static traces, reproduction notes, benchmark summaries.
- `legacy_inputs/` — inventories and selected small docs from old cubes; no bulky PR/source payloads unless explicitly needed.
- `tools/` — scripts for local verification and workpacket creation.
- `manifests/` — content hash and input hash ledgers.

## External inventory

The source bundle is an input, not part of the cube. Future evaluations should read from the external rev0003 bundle or a newer external source bundle, and then write compact evidence back into the datacube.

## Workpacket rhythm

For each candidate or cluster:

1. Pull the row from `data/rev0004_ranked_audit_queue.csv`.
2. Trace the relevant source paths across `3.3.10`, `3.3.x`, and `master`.
3. Check public overlap using `sources/github_open_prs_snapshot_rev0003.csv`, `sources/github_open_issues_snapshot_rev0003.csv`, release notes, and targeted search when freshness matters.
4. Write a small `evidence/<cluster>/<id>.md` file with source lines, branch status, exploit boundary, and recommended next decision.
5. Update the queue row status and only then consider moving anything to the strict document.
