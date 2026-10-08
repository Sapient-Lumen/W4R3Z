# Public evidence portal spec (reproducible, mirrorable, court-usable)

**Track:** A (Deployable core)


> **Goal:** publish results and verification artifacts in a way that survives takedowns, CDN compromise, and post-hoc rewriting attempts.

This spec defines a **static evidence portal** that serves content-addressed bundles with offline verification.

## Principles
- **Content addressed:** every artifact is referenced by hash.
- **Many mirrors:** primary site + independent mirrors (universities, NGOs, parties, courts).
- **Offline verifiable:** a user can download one bundle and verify everything without trusting live endpoints.
- **Minimal dynamic code:** avoid server-side templating and databases for the evidence portal.

## Directory layout (normative)
- `/epb/` — ElectionParameterBundle objects + inclusion proofs
- `/rrp/` — ResultsReleasePackages
- `/alerts/` — DriftAlerts + monitor evidence
- `/tally/` — tally proofs / mixnet transcripts / homomorphic proofs
- `/audit/` — RLA plans, seed beacons, audit reports
- `/keys/` — public keys and rotations (not secrets)

Each object is published as:
- `/<type>/<hash>/manifest.json`
- `/<type>/<hash>/payload.*` (json/xml/pdf)
- `/<type>/<hash>/signatures/`
- `/<type>/<hash>/pbb_anchor/`

## Required portal metadata
The portal root MUST publish:
- `index.json` containing current hashes for:
  - EPB
  - latest FINAL RRP
  - latest checkpointed STH
  - alert index
- `keys.json` listing current signing keys with validity windows
- `mirrors.json` listing official mirrors

## Verification workflow (what users do)
A verifier client should:
1. Fetch `index.json` from ≥2 mirrors and compare hashes.
2. Fetch the referenced objects by hash.
3. Verify signatures.
4. Verify PBB inclusion proofs + witness checkpoint cosignatures.
5. Recompute CRO-derived EVO and ensure UI/API match.

## Publication cadence
- EPB: before polls open
- RRPs: on a fixed interval (e.g., 2–5 minutes) OR on meaningful deltas (policy)
- Alerts: as detected

## “Write once” policy
Once an object is published under a hash path, it MUST never be mutated. Corrections create *new* objects that reference the previous hash.