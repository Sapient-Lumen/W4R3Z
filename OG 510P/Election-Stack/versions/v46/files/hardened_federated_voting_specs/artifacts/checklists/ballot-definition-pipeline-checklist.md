# Ballot definition integrity pipeline checklist

## Inputs (signed legal source bundle)
- [ ] Candidate/measure source documents are collected and versioned.
- [ ] Districting/precinct boundary data is collected and versioned.
- [ ] Filing deadlines and contest eligibility rules are frozen.
- [ ] The legal bundle is signed by the responsible authority and published as a content-addressed artifact.

## Build (deterministic compilation)
- [ ] Ballot Definition is produced in **NIST BD CDF** form (JSON).
- [ ] JSON is canonicalized using **RFC 8785 JCS** (or documented equivalent).
- [ ] `bd_hash = sha256(canonical_bytes)` is computed and recorded.
- [ ] A human-readable render (PDF) is generated from the exact same `bd.json` and hashed.

## Independent reproduction
- [ ] A second independent team compiles from the same legal bundle.
- [ ] Their `bd_hash` matches.
- [ ] Any differences are resolved with a public delta report.

## Ceremony (binding into EPB)
- [ ] The ElectionParameterBundle (EPB) includes `bd_hash` and render hash.
- [ ] EPB is signed by the required multi-party set.
- [ ] EPB is submitted to the Parameter/Key Transparency log and receives inclusion proof.
- [ ] A witness quorum checkpoint is obtained.

## Distribution
- [ ] `bd.json` is distributed via 2+ independent mirrors.
- [ ] Mirrors serve content by hash (content-addressed).
- [ ] Clients verify EPB inclusion+checkpoint before enabling CAST.

## Monitoring
- [ ] Canary retrieval is running from diverse networks.
- [ ] Canary evidence bundles are published if any variance occurs.

## Go/no-go criteria
- [ ] No unresolved BD mismatches.
- [ ] EPB quorum checkpoint achieved.
- [ ] Canaries show no split-view variance.
