# Open-question postures, successor surfaces, and live-focus sync

DelayBasin already keeps a durable `RESOLUTION-LEDGER.json`, an operator-facing open-question registry, a trajectory map, a compact `context-pack.json`, and a derivative `frontier-ticket.json`.
That stack is useful only if those surfaces agree on a simpler truth:

**once an open question is actually resolved in the durable ledger, operator-facing discovery surfaces should stop advertising it as unresolved live work and should instead point toward the successor surface or reopen trigger that now carries the work.**

This is stronger than saying every resolved question must disappear.
It is weaker than claiming DelayBasin needs a question court, issue tracker board, or workflow controller.

## Practice / observation

The recent compact-surface stack exposed a concrete drift mode:
- the resolution ledger already marked several questions as resolved,
- the open-question registry still said some of those questions were `unresolved`,
- the trajectory map still echoed some of the same stale postures,
- `context-pack.json` then selected the last visible question row without excluding resolved ones,
- and `frontier-ticket.json` inherited that stale selection as if it were the current live frontier.

That is not just a prose mismatch.
It changes what a future careful pass is likely to inspect first.

The missing question is therefore narrower than “how do we manage all questions?”
It is:

**what compact public rule keeps resolved-question posture, successor surfaces, and frontier selection synchronized once the archive already has durable closure truth?**

## Pressure from neighboring datacubes

Several neighboring cubes push in the same direction.

- **VHK** keeps ticket-spine and handoff extractors honest about what currently owns the work rather than leaving later operators to infer ownership from stale surrounding narrative.
- **EvidenceVault** keeps compact projections subordinate to their governing retained audit surfaces rather than letting a projected summary silently outrank the underlier it came from.
- **Micromax** repeatedly pressures tiny visible handles and adjacent exact-inspect surfaces to understand the same public token instead of forcing a second reconstruction step.
- **Anonymity** pressures verifier-card and worked-route surfaces to preserve the current answer path rather than a flattering stale route.

DelayBasin already has the same ingredients:
- a durable closure ledger,
- operator-facing discovery surfaces,
- and compact derivative handoff packets.

What was still under-specified was the **sync rule** between them.

## Working synthesis

A useful current synthesis is:

> DelayBasin should preserve one compact **open-question posture / successor-surface / live-focus sync** rule whenever `RESOLUTION-LEDGER.json` already marks a question resolved but operator-facing discovery surfaces still expose that question as unresolved or current frontier. The rule should require the registry and trajectory surfaces to say the question is resolved when they still mention it, to name the successor surface or reopen route, and to keep `context-pack.json` plus `frontier-ticket.json` from surfacing a resolved question as live focus.

In practice, that means:
- `RESOLUTION-LEDGER.json` remains the closure underlier;
- `docs/20-constitution/open-question-registry.md` may keep the question visible, but not as unresolved once closure is durable;
- `docs/00-meta/trajectory-map.md` may keep the question visible, but not as live current posture once closure is durable;
- `context-pack.json` should select from unresolved open questions only;
- `frontier-ticket.json` should surface the last source-backed unresolved hot question rather than the last recently mentioned resolved one.

## Countermodels / probes

1. **Registry-memory countermodel**
   - A question may stay marked unresolved only because no one refreshed the nearby prose.
   - Probe: compare current registry posture against the durable resolution row before packaging.

2. **Trajectory-echo countermodel**
   - The trajectory map may keep echoing an older live posture after the underlier closed.
   - Probe: if the trajectory still mentions the question with a current-posture row, require that row to say resolved and point toward the successor surface or reopen condition.

3. **Frontier-glow countermodel**
   - The compact frontier packet may simply pick the last vivid question instead of the last unresolved one.
   - Probe: fail closed if `context-pack.json` or `frontier-ticket.json` surface an OQ that the resolution ledger already marks resolved.

4. **Over-systematization countermodel**
   - DelayBasin may be reaching for an issue tracker or question court it does not need.
   - Probe: keep the repair small — a sync rule and fail-closed checks, not a standing governance board.

## Design consequence

The archive does **not** need a question court.
It does need one answer-honest rule:

- resolved questions may remain visible,
- but they must not remain visibly **unresolved** on operator-facing discovery surfaces,
- and they must not stay selectable as the current live frontier once durable closure exists.

That is enough for canon now.
The stronger issue-board / question-court / workflow-controller story remains outside canon.
