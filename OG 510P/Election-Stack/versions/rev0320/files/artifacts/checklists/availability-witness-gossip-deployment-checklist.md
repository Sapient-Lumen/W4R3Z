# Availability Witness Gossip Deployment Checklist

**Track:** Shared (cross-cutting)


## Governance
- [ ] Publish AWG parameters (peer count N, period T, quorum policy) inside the ElectionParameterBundle.
- [ ] Maintain an explicit list of witness public keys and organizational affiliations.
- [ ] Require diversity constraints for quorum (classes/jurisdictions).

## Implementation
- [ ] Implement `AvailabilityGossipMessage` signing and verification.
- [ ] Bound `recent_entries` size and enforce rate limits.
- [ ] Embed latest ATL checkpoint in evidence endpoint responses (headers).
- [ ] Provide offline verifier support for checkpoint + witness bundle.

## Operations
- [ ] Set up at least 3 independent witness operators with distinct infrastructure providers.
- [ ] Run a daily “gossip health” report (missing peers, latency, divergence).
- [ ] Test split-view simulation quarterly (partition + selective suppression).

## Incident behavior
- [ ] Define MAAD and alarm thresholds.
- [ ] Ensure missed-MAAD triggers publication of `SuppressionSuspicion`.
- [ ] Ensure URP generation is automated when checkpoint fetch fails.
