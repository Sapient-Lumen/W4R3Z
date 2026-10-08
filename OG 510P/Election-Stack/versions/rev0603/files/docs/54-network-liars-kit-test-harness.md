# 54 — “Network liar’s kit” test harness — draft

**Track:** A (Deployable core)


## Purpose
Prove the system fails *loudly* when the network lies, rather than failing silently.

## Required simulations
1. **Stealth traffic diversion**: reroute a subset of users via hijack-like conditions.
2. **DNS takeover**: redirect Relay/Gateway hostnames.
3. **CA misissuance**: serve a valid-but-wrong cert chain to a subset of clients.
4. **Partial partitions**: isolate subsets of witnesses and gateways.
5. **Targeted L7 throttling**: degrade a region’s submission capacity.

## Pass conditions (minimum)
- Clients do not display “RECORDED” unless inclusion proof verifies.
- Witness quorum checkpoints diverge → `ForkProof` produced and published.
- Intake receipts expire → voter can publish evidence of non-inclusion.
- Public status page is updated with signed incident statements.

## Tooling suggestions
- Use multiple independent measurement vantage points (commercial and academic).
- Publish replayable traces and expected outputs as part of the Evidence Bundle.

## References
- RPKI best practices and lessons learned
- Stealthy hijacking draft (incomplete ROV adoption)