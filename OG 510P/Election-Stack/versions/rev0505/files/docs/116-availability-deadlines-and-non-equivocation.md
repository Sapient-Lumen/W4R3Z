# Availability deadlines and non-equivocation

**Track:** A (Deployable core)


## MAAD
Maximum Availability Attestation Delay (MAAD):
- If a monitor detects an outage/split view, an ATL entry must be anchored within MAAD.

## Why
Without a deadline, suppression becomes a “he said / she said.”

## Non-equivocation notes
Gossip alone can be delayed; consider:
- cross-anchoring ATL checkpoints into independent logs
- independent timestamping for final bundles

## Normative requirements
- **MUST** publish MAAD.
- **MUST** treat MAAD violation as a publishable incident.