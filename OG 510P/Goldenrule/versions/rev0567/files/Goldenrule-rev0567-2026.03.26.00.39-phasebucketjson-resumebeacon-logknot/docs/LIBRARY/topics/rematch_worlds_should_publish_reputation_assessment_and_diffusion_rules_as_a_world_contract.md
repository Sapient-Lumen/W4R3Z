# Rematch worlds should publish reputation assessment and diffusion rules as a world contract

Once a rematch or partner-choice world lets reputation travel across encounters, cooperation is no longer governed only by bilateral payoffs.
The **reputation system itself** becomes part of the institution.

That means Concord should not hide reputation mechanics inside controller code or wide transient reports.
One compact retained contract is enough.

Recent external work reinforces this framing.
`RS-GR-041` treats reputation as the aggregation of peer assessments diffused through a social network, and its performance depends on the assessment rule, the data flow, the latency/noise in the feedback channel, and the network topology.
For Concord, the inheritor-facing consequence is simple: if those pieces differ, the world has changed.

## Minimum contract

If a world carries reputation across matches or uses it for matching / sanctions / access, publish at least:

1. the **visibility rule** (`public`, `private`, `local-neighborhood`, or declared equivalent),
2. the **assessment rule** (how actions update reputation and whose reports count),
3. the **diffusion topology** (broadcast, neighborhood gossip, mediator-only, or other declared graph),
4. the **latency / noise / decay rule** for reputation signals,
5. and the **decision hooks** that actually consult reputation (partner selection, punishment, admission, tie-breaking, etc.).

## Implementor consequence

Do not compare reputation-bearing rematch worlds as if they shared one institution when these five fields differ.
A change in reputation visibility, gossip reach, or update noise is not just a controller tweak; it changes what reciprocity means in that world.

## Archive consequence

Keep this compact.
Retain one tiny reputation-contract section in the nearest benchmark artifact or receipt rather than carrying a fresh report pair each time a reputation variant is explored.
