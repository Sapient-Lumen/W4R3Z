
# Action rehearsal candidate contract v0

Purpose: name a small honest surface for “show me what is about to happen” without pretending perfect prediction.

A **rehearsal card** is a shell-owned preflight surface for a strong action, route, restore, or Flow entrypoint.
It is not a guarantee engine.
It is a compact witness of the shell's current best knowledge.

## Candidate posture

1. **Rehearsal is shell-owned**
   - it should compose with Omnibox, Preview-adjacent actions, Exchange route proposals, Recall restore, Desktop Flow, and reviewed shell actions

2. **Rehearsal is exact about what it knows**
   - exact subject / packet / anchor
   - chosen route / provider / template when already known
   - known effects
   - repair or uncertainty surfaces when exactness is not available

3. **Rehearsal is not silent execution**
   - opening a rehearsal card is not the same as committing the action
   - stronger actions still require the same review or receipt pathways they would require elsewhere

4. **Rehearsal is compositional**
   - a seed may open a rehearsal card
   - a result card may deepen into a rehearsal card
   - a Flow entrypoint may emit a rehearsal card before commit

5. **Rehearsal admits uncertainty honestly**
   - exact
   - repaired
   - partial
   - unavailable
   - deferred-to-runtime

## Candidate uses

- show the route that an Exchange action would take before commit
- show which objects a seed will expand against
- show what a capsule restore will try to bind and what will need repair
- show what packet a Flow entrypoint will inject into the graph
- show one compact denial or risk note before a strong action proceeds

## Candidate v0 specimen

A narrow specimen could be:
- one Omnibox result that deepens into a rehearsal card,
- one capsule restore rehearsal,
- one Exchange route rehearsal,
- and one Desktop Flow entry rehearsal.

## Guardrails

- do not claim perfect determinism
- do not let rehearsal become a giant simulation platform before one compact specimen exists
- do not hide provider identity, route choice, or uncertainty class
- do not let cards bypass the existing reviewed-action and receipt story

## Working stance

Rehearsal looks like one of the most promising ways to make Helm feel unusually trustworthy and unusually powerful at the same time.
It should remain a candidate contract until one good specimen proves it is more than beautiful UI theory.
