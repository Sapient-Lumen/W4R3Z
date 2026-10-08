# Resilio incident-object absence, history search, and diagnostic-continuity fragmentation evaluation

## Why this seam matters

The archive already has stronger row meaning, route choice, affected-item proof, evidence bundles, and escalation packets.
What still remains too article-shaped is the ordinary operator experience between those pieces.
After one failing row appears, the next real question is no longer only `what should I click next?`
It becomes:

- what investigation am I in now
- what have I already checked
- which explanation is currently strongest
- what proof is still missing
- whether another route or heavier capture is actually justified
- what conclusion should survive handoff, restart, or tomorrow's reopening

Current official Resilio docs are candid about the pieces of diagnosis.
They are still weak at owning the investigation as one durable object.

## What current official Resilio still gets right

Current official material still openly admits that diagnosis is multi-surface work.
That candor is useful.

Examples the docs still publish now:

- **The main view is only part of the answer.** The current desktop main-view article still says History is a separate 30-day activity surface, that statuses show current activity, and that `X of Y` opens the peers list.
- **Troubleshooting is route-shaped.** The current `My files don't sync` article still tells operators to click peers counts, click status warnings that often lead to KB explanations, search Sync History, open peers lists to inspect upload/download queues, and only then work through a broad checklist.
- **Item-level detail is separate from row meaning.** The current `Locked files` article still says the error row opens the locked-file list and allows path jump-through.
- **The current product still lacks some in-row affordances and fixes them piecemeal.** The live v3 change log still records that `Can't download file` had to be fixed to be clickable, and still shows the active line through `3.1.2.1076`.
- **Heavy evidence capture is a separate ritual.** Current log guides still say debug logging must be enabled, Sync should be restarted to ensure it is active, logs should be collected for at least 15 minutes, and the operator may need all-peer logs, manual attachment, or fallback routes.
- **Support lane itself is conditional.** Current debug-log guides still say direct technical support is only for Resilio Sync Business customers and that Sync v3 users are directed toward forum/help-center self-service for functionality issues.

That is all refreshingly candid.
Resilio is not pretending that one row is one complete diagnosis.

## Where the current contract still fails

### 1. There is still no durable incident home

The operator can open a row, a peers list, a history search, a queue, a locked-file list, and later a log guide.
But the product still does not publish one durable object that says:

- this investigation started from *this* row
- these routes were already tried
- this explanation is currently strongest
- these alternatives remain live
- this is the next cheapest unresolved question

Without that object, diagnosis is remembered socially or mentally rather than carried by the product.

### 2. Chronology is still split across unrelated surfaces

Current docs still distribute time-bearing truth across:

- a current row
- a 30-day history surface
- peer presence checks
- queue state
- later support/log reproduction windows

That makes the ordinary answer to `what happened first, what changed after I intervened, and what is still current?` too easy to lose.

### 3. Evidence sufficiency still collapses into folklore

The current troubleshooting pattern still makes it easy to jump from:

- row click
- history search
- peer/queue checks

to:

- `collect the logs from all peers`

without one product-owned page that says what heavier capture would actually add, which current explanation it would strengthen or falsify, and whether the remaining gap is worth the cost.

### 4. Handoff continuity is still weak

If one operator checks row meaning and another later checks logs, the product still does not leave one durable explanation receipt that preserves:

- the winning explanation so far
- the alternatives explicitly not ruled out
- the exact gap blocking a stronger claim
- the condition for reopening or escalating

That is too much narrative loss for an ordinary sync failure.

## What AnonSync should do instead

AnonSync should keep the candor and refuse the investigation sprawl.
The product should own four ordinary page families for this seam:

1. **Diagnostic incident page**
   - investigation headline
   - current best explanation
   - live alternative explanations
   - missing-proof budget
   - next cheapest diagnostic question

2. **Incident timeline page**
   - current row/token entry
   - relevant history events
   - route hops taken
   - operator actions and aftermath
   - freshness / decay horizon

3. **Evidence sufficiency review page**
   - what the current evidence already supports
   - what heavier capture would add
   - what can be closed now
   - what must escalate now

4. **Diagnostic conclusion receipt page**
   - winning explanation
   - rejected or still-live alternatives
   - supporting evidence set
   - stronger forbidden sentence
   - reopen / escalation boundary

## Sharper non-clone line

So the tighter conclusion for this pass is:

> Resilio is still worth borrowing for its candor that diagnosis spans rows, peers, history, queues, item lists, and heavier evidence capture. But it is not worth cloning the way the ordinary operator still has to remember the investigation as a mental story rather than reopen one durable case object that preserves what has already been checked, what remains missing, and what conclusion is actually justified.

## New replacement pages added in this revision

- `732` Diagnostic incident page
- `733` Incident timeline page
- `734` Evidence sufficiency review page
- `735` Diagnostic conclusion receipt page
