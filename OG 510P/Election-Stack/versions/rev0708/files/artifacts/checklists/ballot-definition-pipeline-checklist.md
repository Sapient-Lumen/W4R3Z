# Ballot definition integrity pipeline checklist

**Track:** Shared (cross-cutting)


## Inputs (signed legal source bundle)
- [ ] Candidate/measure source documents are collected and versioned.
- [ ] Districting/precinct boundary data is collected and versioned.
- [ ] Filing deadlines and contest eligibility rules are frozen.
- [ ] The legal bundle is signed by the responsible authority and published as a content-addressed artifact.

## Build (deterministic compilation)
- [ ] Ballot Definition is produced in **NIST BD CDF** form (JSON).
- [ ] JSON is canonicalized using **RFC 8785 JCS** (or documented equivalent).
- [ ] `bd_hash = sha256(canonical_bytes)` is computed and recorded.
- [ ] If a human-readable render is produced (PDF), it is generated from the exact same `bd.json`, hashed, and treated as **derivative** (review aid, not the API).
  - [ ] The render includes `bd_hash` + a pointer to the canonical `bd.json` (prevents silent drift).
  - [ ] The canonical publication remains the machine-readable `bd.json` + `bd_hash` (no “PDF-only” publication).

## Independent reproduction
- [ ] A second independent team compiles from the same legal bundle.
- [ ] Their `bd_hash` matches.
- [ ] Any differences are resolved with a public delta report.

## Ceremony (binding into EPB)
- [ ] The ElectionParameterBundle (EPB) includes `bd_hash` (and MAY include the render hash if a render is published).
- [ ] EPB is signed by the required multi-party set.
- [ ] EPB is submitted to the Parameter/Key Transparency log and receives inclusion proof.
- [ ] A witness quorum checkpoint is obtained.

## Distribution
- [ ] `bd.json` is distributed via 2+ independent mirrors.
- [ ] Mirrors serve content by hash (content-addressed).
- [ ] Publication is MAPT-passable: a third party can fetch+verify `bd.json` quickly (bounded index/digest card if needed; see `docs/187` + `docs/206`).
- [ ] Clients verify EPB inclusion+checkpoint before enabling CAST.

## Monitoring
- [ ] Canary retrieval is running from diverse networks.
- [ ] Canary evidence bundles are published if any variance occurs.

## Go/no-go criteria
- [ ] No unresolved BD mismatches.
- [ ] EPB quorum checkpoint achieved.
- [ ] Canaries show no split-view variance.
