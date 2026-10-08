# Unreachability proofs (URPs)

**Track:** A (Deployable core)


## Purpose
Provide a portable, court-usable object that supports claims like:
- “Endpoint X was unreachable from cohort C during window W.”

## Structure
`UnreachabilityProof` includes:
- targets and time window
- probe cohort definition
- raw result hashes
- reduced statistics (success rates, latency quantiles)
- signatures

See `schemas/UnreachabilityProof.json`.

## Normative requirements
- **MUST** include multiple vantages.
- **MUST** include control targets (known-good endpoints) to reduce false attribution.
- **MUST** be reproducible from raw results + reduction code.