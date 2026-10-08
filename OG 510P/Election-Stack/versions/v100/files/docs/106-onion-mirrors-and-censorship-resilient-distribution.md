# Onion mirrors and censorship-resilient distribution

**Track:** A (Deployable core)


## Goal
Ensure the public can fetch evidence bundles even under:
- DNS tampering
- IP blocking
- selective throttling

## Onion mirror profile
- run a read-only mirror of evidence bundles as an onion service
- publish the onion address inside signed bundles and checkpoints

## Normative requirements
- **SHOULD** provide at least one onion mirror for evidence bundles.
- **MUST** treat onion mirrors as *read-only*: no intake endpoints.
- **MUST** pin onion addresses in signed parameter bundles (EPB) to prevent substitution.

## Notes
Onion mirrors don’t solve all censorship, but they raise attacker cost and provide alternative paths.