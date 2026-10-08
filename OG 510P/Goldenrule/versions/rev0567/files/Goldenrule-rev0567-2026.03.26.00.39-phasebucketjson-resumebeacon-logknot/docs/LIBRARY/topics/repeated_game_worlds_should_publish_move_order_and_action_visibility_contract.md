# Repeated-game worlds should publish move order and action visibility contract

Recent direct-reciprocity theory adds a compact warning for future Concord world design.

- `RS-GR-133` studies a leader-follower transformation of repeated two-player games.
- The paper shows that some simple memory-1 simultaneous-move equilibria remain stable when one player openly commits or moves first.
- But that reassuring transfer does **not** automatically extend to richer action sets or longer-memory equilibria.

## Why this matters for Concord

A world where players move simultaneously is not the same scientific object as a world where:

- one player moves first,
- one player observes the other's current move,
- one player can openly signal or commit,
- or leadership alternates / is randomly assigned.

If Concord eventually studies apology, repair, disclosure, signaling, or role asymmetry, then move order and action visibility stop being interface details and become part of the world contract.

## Minimal contract fields

Any sequential or disclosed-action benchmark lane should publish at least:

1. move order (`simultaneous`, `leader_follower`, `alternating`, or richer declared mode),
2. what is visible before the second move,
3. whether first-mover actions are binding commitments, noisy signals, or revocable previews,
4. how roles are assigned and whether they persist across rounds / rematches,
5. and whether benchmark comparisons pool sequential and simultaneous lanes or keep them separate.

## Implementor handoff

After the first leave/rematch world is live, add one small sequential/disclosed-action companion lane before making broad claims that a strategy is robust across institutions.
