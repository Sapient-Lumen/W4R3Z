# Censorship & partition drill

**Track:** Shared (cross-cutting)


## Goals
- Validate that selective dropping is detectable
- Validate that clients show truthful state (PENDING vs RECORDED)
- Validate offline fallback messaging

## Steps
1. Induce partition: block a region from reaching primary sequencer
2. Submit ballots via alternate entrypoints
3. Force intake receipts without inclusion
4. Verify evidence generation and publication
5. Confirm witness gossip detects split views (if simulated)
6. Confirm incident comms template triggers and the offline fallback path is available
