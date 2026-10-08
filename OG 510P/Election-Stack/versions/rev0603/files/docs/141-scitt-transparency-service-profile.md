# SCITT transparency service profile for election evidence

**Track:** A+C (Core + North Star)


## Goal
Provide an optional, standards‑aligned way to **register signed election evidence** in a transparency service that is independent of the election operator.

SCITT (Supply Chain Integrity, Transparency, and Trust) defines how signed statements can be registered in a transparency service and later verified.

This profile applies SCITT concepts to election evidence objects:
- Election Parameter Bundles (EPB)
- Witness‑quorum Checkpoints
- Evidence Bundle Manifests
- Results Release Packages
- Outage/Parity/Drift/Fork alerts

## Design principles
- Evidence is **signed before registration**.
- Registration produces an immutable receipt (inclusion/consistency proof style).
- Relying parties MUST NOT assume statement ordering implies issuance ordering unless stated by the service policy.

## Profile requirements
### Statement format
A SCITT Signed Statement payload MUST include:
- `type` (e.g., `epb`, `checkpoint`, `rrp`, `alert`)
- `context` (election_id, jurisdiction_id, epoch)
- `hash` (content address of canonical bytes)
- `prev_hash` (optional for chaining)

### Registration policy
The election must publish a **Transparency Service Registration Policy** describing:
- which evidence types MUST be registered
- maximum registration delay (MRD)
- how receipts are published

### Receipt publication
Receipts MUST be included in the public evidence portal and referenced by:
- PBB checkpoints
- ATL checkpoints

### Key separation
Keys used for SCITT statements MUST NOT be reused for other signing purposes.

## Interop
If a SCITT Reference API (SCRAPI) is available, implementers SHOULD support:
- submitting a statement
- retrieving a receipt
- querying by content hash
