# Results API contract (template)

**Track:** Shared (cross-cutting)


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
- `err_cdf_version` (e.g., NIST ERR CDF; see `source: nist_sp1500_100r2_err_pdf`)
- `canonicalization` (e.g., RFC8785 JCS; see `source: rfc8785_txt`)

## Semantics
- Numbers MUST be derived from the CRO referenced by `cro_hash`.
- If `checkpoint_id` is stale beyond policy, client MUST show “verification delayed.”
