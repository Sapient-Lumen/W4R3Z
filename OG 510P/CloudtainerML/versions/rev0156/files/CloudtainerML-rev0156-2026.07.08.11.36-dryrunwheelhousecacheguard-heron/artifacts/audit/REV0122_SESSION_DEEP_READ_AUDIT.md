# Session deep read audit — REV0122

Status: `pass_with_blockers`  
Promotion allowed: `false`

## Heart

CloudtainerML is a claim compiler: architecture claim -> hostile falsifier -> exact receipts -> named-hardware decision.

## Missing

- `real immutable TinyLlama trace NPZ/provenance`
- `digest-authenticated complete TinyLlama snapshot proof`
- `accepted selector/evaluation receipts on real trace`
- `named-hardware sparse-vs-dense timing`
- `strong baseline bracket`
- `stop/pivot memo`

## Severe/wasteful findings

- `evidence_lane_gravity`: gate construction continues to outrun decisive evidence
- `snapshot_hash_gap`: hash verification was optional and the intake hash flag was not wired into inspect_snapshot
- `metadata_drift`: top-level metadata audits miss stale lower-salience fields such as codename/highlight/current_primary_change
- `tracked_pycache`: generated Python bytecode was packaged and checksummed
- `fixture_archaeology`: duplicated handoff/tamper fixture trees consume attention and bytes
