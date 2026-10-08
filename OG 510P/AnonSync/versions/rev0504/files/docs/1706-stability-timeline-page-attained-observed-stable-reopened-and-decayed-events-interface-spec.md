# Stability timeline page — attained, observed, stable, reopened, and decayed events

## Purpose

This page gives the operator a chronological view of how an attained effect did or did not become stable.
It exists so the product can show when the effect merely landed, when observation began, what restarted the clock, what earned promotion, and what later reopened or decayed the claim.

## Required event classes

The timeline must distinguish at least:

- attainment earned
- observation window started
- observation paused
- observation restarted
- connected-cohort stable only
- required cohort entered observation
- material regression detected
- narrow reopen
- full reopen
- stability earned
- stability decayed
- stability re-earned

## Required event payloads

Each event must carry:

- timestamp and trusted time basis
- actor or system source
- cohort affected
- whether the event strengthens, weakens, or merely annotates the claim
- whether the event resets the dwell clock
- strongest blocked sentence after the event

## Required event examples

The page must be able to render events like:

- `attainment earned for connected cohort only`
- `offline required participant still missing; observation continues but stable promotion blocked`
- `late offline writer returned and overwrote online state; full reopen triggered`
- `manual Archive restore performed while Sync was stopped; later rescan re-archived older version and reset stability clock`
- `watcher exhaustion detected; future changes may surface only on periodic rescan`
- `full required cohort observed clean through dwell window; stability earned`

## Timeline interpretation rules

- a calm interval is never enough unless the page also knows who remained able to reopen it
- a reopen event must preserve earlier earned states as historical events rather than rewriting the past
- decay is different from supersession: decay weakens the same stability claim, while supersession may replace it with a newer one
- connected-only calm must stay visibly weaker than required-cohort stability
- the viewer must always be able to tell whether the next likely move is promotion, continued observation, or downgrade
