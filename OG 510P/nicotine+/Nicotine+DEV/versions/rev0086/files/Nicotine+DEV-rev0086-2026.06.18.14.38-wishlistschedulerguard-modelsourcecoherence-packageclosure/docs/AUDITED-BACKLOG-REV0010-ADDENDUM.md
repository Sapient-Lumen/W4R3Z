# Audited backlog addendum — rev0010

## Main movement

PB-01 moved forward materially. U-168 and U-176 are no longer vague peer-binding backlog rows; together they are a strict/front-lane report-candidate with a reproducible state-machine probe across `3.3.10`, `3.3.x`, and `master`.

## Queue changes

- **U-168**: promoted into PB-01 as direct PeerInit replacement behavior.
- **U-176**: promoted into PB-01 as secondary post-init primary-promotion behavior.
- **U-165**: retained as PierceFireWall support/precondition context, not a standalone report.
- **U-171**: retained as address/server-trust hardening backlog.
- **U-181**: retained as queue/backpressure backlog.
- **U-40**: merged/aliased into **U-145** to avoid duplicate address-validation work.
- **U-205**: remains an alias of **U-145**.

## Strict document status

The strict document now has **2 report-candidates** and **0 production-ready disclosure texts**:

1. U-123 transfer-token/F-session orphaning.
2. PB-01 / U-168+U-176 peer-connection primary election.

## Backlog caution

The Pass 195 `fresh-unmentioned` label remains a seed hypothesis. Every item still needs hard public-overlap checking, source-lane checks, and coherence review before strict/front-lane movement.
