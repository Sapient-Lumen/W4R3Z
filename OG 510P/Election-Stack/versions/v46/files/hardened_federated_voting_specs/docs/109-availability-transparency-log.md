# Availability Transparency Log (ATL)

**Track:** A (Deployable core)


## Goal
Make availability failures **auditable** and not dismissible.

When the system is unreachable or split-delivered, produce signed artifacts that:
- identify which endpoints were affected
- include multi-vantage probe evidence
- anchor to a checkpoint chain

## Structure
ATL is an append-only Merkle log with:
- Signed Tree Heads / checkpoints
- inclusion + consistency proofs

Entries include:
- `AvailabilityProbeResult`
- `OutageAttestation`
- `ParityReport`
- `DriftAlert` / `ForkProof`

See `schemas/AvailabilityTransparencyEntry.json`.

## Deadlines
Define Maximum Availability Attestation Delay (MAAD):
- within MAAD of an outage detection, an attestation must be anchored

## Normative requirements
- **MUST** operate ATL with witness quorum countersigning.
- **MUST** allow independent monitors to mirror and audit ATL.
- **MUST** publish an availability SLO and escalation policy.