# 07 — Vote Catalog (v0.19)

All votes are intended to be **tiny** and **decisionful**.

## “Amazing” votes (default keepers)
- `floor{A#=...}` doubles as **integrator selection** (winner is integrator by default).
- `patch{P#=stars,...}`: select canonical next change
- `floor{A#=stars,...}`: choose who gets next extra slice / integration
- `lease{scope->A#=stars}`: choose owner for hot scope (or request lease)
- `hot{ID=stars,...}`: promote items into global hot
- `ce_admit{CE#=stars,...}`: spend budget to attempt certification
- `checks{V#=stars,...}`: which verifiers/tests to run next
- `compact{yes=stars,no=stars}`: trigger WS compaction now
- `zoom{ID=stars}` (rare): request expanded view of one item (P2+)

## Votes to defer (early)
- protocol elections (vote on the protocol every run)
- micro-claim wording votes
- persistent reputation votes (politics/drift)
- proxy/delegation chains beyond simple lease/floor

## Dissent requirement (anti-consensus-collapse)
Each agent is encouraged (or required in some modes) to produce:
- one agreement, one disagreement/concern, even if brief.
This is content, not a vote; votes remain scarce.
