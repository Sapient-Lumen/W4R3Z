# Results API contract (template)

> Publish this **before polls open** and pin it by hash in the EPB.

## Endpoints
- `GET /index.json` → pointers to latest hashes
- `GET /enr/latest` → EVO + `cro_hash` + `checkpoint_id`
- `GET /cro/{hash}` → canonical results object
- `GET /rrp/{hash}/manifest.json` → release package manifest
- `GET /alerts/{hash}` → DriftAlert

## Required fields (every response)
- `election_id`
- `cro_hash`
- `checkpoint_id`
- `unofficial` boolean

## Semantics
- Numbers MUST be derived from the CRO referenced by `cro_hash`.
- If `checkpoint_id` is stale beyond policy, client MUST show “verification delayed.”
