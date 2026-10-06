# Frontier tickets, selected-focus handoffs, and live open-work cards

## Practice / observation

DelayBasin now preserves a fair amount of honest current-state detail:
- durable state in ledgers and queues,
- `action_lane` on many live rows,
- `gate_class` on many discharge-bearing rows,
- basis witnesses for what was actually reread,
- and status-lane witnesses for what is admitted, materialized, and frozen enough to cite.

That solves several real continuity failures, but it leaves one smaller seam behind.
A future careful pass can still land honestly and still have to **scan several live surfaces before it knows what the archive currently treats as the live focus**.

`context-pack.json` already helps, but it remains a compact caution-and-open-work packet rather than a visibly selected handoff card.
It says what is hot enough to keep nearby.
It does not yet say what current careful work should most naturally look at first.

## Pressure from neighboring datacubes

Several neighboring datacubes apply pressure here.

`VHK-rev0419` keeps a compact selected work ticket so a later operator does not have to reconstruct the active lane from many runtime/control surfaces.
`Anonymity-rev0547` keeps worked routes and handoff cards explicit enough that later terse surfaces can still recover what current bridge is doing.
`Micromax-rev0523` keeps visible action rows honest about what Enter will actually do, which pressures DelayBasin not to make a future operator infer the current live focus from scattered supportive cues alone.
`DeriveBSD-rev0391` keeps official support handoff timeline-first, which pressures DelayBasin to keep one tiny current orientation card rather than forcing fresh readers to rebuild the same handoff from raw bundle parts.

The common pressure is not “import a queue controller.”
The common pressure is that once an archive already keeps durable state and compact derivative packets, it may also deserve one **tiny selected-focus handoff card** that still points at unresolved live work rather than a stale answered question.

## External pressure from handoff practice

Outside DelayBasin, incident and handoff practice often benefits from one small orientation surface that says current state, current focus, and immediate next context rather than making the receiver reconstruct that from many receipts, status widgets, and working notes.
That pressure supports a bounded take here as long as DelayBasin keeps the card derivative and source-backed.

## Working synthesis

DelayBasin should import only the smallest derivative take:

- keep one compact `frontier-ticket.json` as a **selected live-focus handoff card**,
- let it inherit the current posture from `SURFACE-STATUS.json` and `context-pack.json`,
- let it select one source-backed current focus from the already-admitted hot open-question slice,
- let it carry only a tiny background continuity check from the latest live obligation and latest cooling retrospective,
- and keep the whole surface explicitly derivative rather than constitutional.

The point is not to replace canon.
The point is to reduce one repeat recovery error:

> a future careful pass lands honestly, but still has to reconstruct what the archive currently treats as the live frontier by scanning multiple source-backed surfaces that already agree enough to support one tiny handoff card.

## Frontier ticket vs action lane vs context pack vs broader queue court

- **Action lane** preserves the next-step class on a particular durable item.
- **Gate class** preserves what kind of future event would legitimately change that item.
- **`context-pack.json`** preserves a compact caution-and-open-work packet.
- **`frontier-ticket.json`** preserves one selected live focus plus one tiny continuity background so a fresh pass knows what to inspect first.
- **A broader queue court** would classify, prioritize, and route many more work types than DelayBasin has earned.

So the frontier ticket is not a replacement for action lanes, not a replacement for the context pack, and not permission to grow a scheduler, dashboard, or queue-state controller.
It is a one-read handoff card.

## Design consequences

When DelayBasin keeps a frontier ticket, it should preserve:

- the **derivative status / explicit non-authority note**,
- the **selection policy / what source-backed rule picked the current focus**,
- the **current posture / live-vs-frozen state that still matters for handoff**,
- the **selected primary focus / exact governing surface and source-backed compressed text**,
- the **background checks / latest open obligation and latest cooling retrospective kept nearby for continuity**,
- and the **reentry anchors / where a careful pass should reopen canon before treating the derivative card as trusted guidance**.

This keeps the card small and source-backed.
If the card and its sources disagree, the card should fail closed and be regenerated.

## Countermodels / probes

Possible failure modes are straightforward:

- the card merely duplicates `context-pack.json` without clarifying what to inspect first,
- the archive starts pretending one selected focus is constitutionally binding rather than a derivative handoff choice,
- the card silently becomes a priority controller or queue court,
- or the selection policy becomes so vague that the same archive state yields different “current focus” cards by mood.

Those are reasons to narrow or retire the card, not reasons to skip a bounded test entirely.

## Transformer-facing implication

If DelayBasin is partly functioning as a bounded continuation substrate, then continuity quality may depend not only on preserving durable state, but also on preserving one tiny **current-focus orientation surface** for the next reentry.

The weaker implication is not that DelayBasin has discovered a real workflow engine.
It is this:

**long-horizon archive prompting may benefit from one explicit derivative current-focus card that reduces reentry scan cost and handoff ambiguity without pretending that one card replaces the canon, the ledgers, or the current status constitution.**
