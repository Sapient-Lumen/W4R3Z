# Cooperation benchmark programs should ship a lineage-grouped macro review queue for compact cards

When compact cooperation benchmark cards already have a flat review queue, future inheritors should not have to reconstruct one lineage's live repair state by scanning many queue rows and guessing which command is the best next action.

A small lineage-grouped macro review queue is worth shipping once the archive already has:

1. a flat actionable review queue,
2. lineage heads,
3. and a citation surface whose admissibility can be blocked by more than one live issue at once.

The grouped surface should stay derivative rather than becoming a second review system.
It should reuse the flat queue items, but regroup them by lineage and publish the union of item ids, item kinds, reason codes, context paths, review commands, and repair commands for that lineage, plus one deterministic primary review command.

That keeps handoff and control-plane surfaces from silently collapsing multi-item repair state into one arbitrary command, which is the exact failure mode the grouped surface prevents.
