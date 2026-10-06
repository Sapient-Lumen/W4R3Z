# Action lanes, primary next-step routing, and discharge budgets

## Practice / observation

DelayBasin already preserves compact public **state** on most durable queue and ledger items, but the **next-step class** for those same items often still lives only in discharge prose. That leaves later passes to reread similar strings and reconstruct whether the item is mainly waiting to be promoted, replaced, retested, rereviewed, narrowed, validated, or simply kept compact.

That is a smaller problem than a full queue-code court, but it is still a real one. Two items can share a similar discharge shape while meaning different next steps, and one item can accumulate stylistic rewrites of the same route without ever saying that the underlying routing class stayed the same.

## Pressure from neighboring datacubes

Several neighboring datacubes apply real pressure here.

`VHK-rev0349` keeps a compact `action_lane` on queue items so review debt can be triaged as a stable next-step class rather than only narrated in prose. `pyCausalWeave-rev0082` keeps small typed problem and repair labels so coordination failure does not drift into local wording dialect. `Micromax-rev0408` keeps actionability and blocker posture explicit enough that “needs work” does not hide what kind of work is actually next.

The common pressure is not “import a giant controller.” The common pressure is that once a durable item already has identity, state, and discharge prose, it may also deserve one compact public label for the **primary next step**.

## External pressure from adjacent queue and issue practice

Outside DelayBasin, issue trackers, maintenance queues, and audit ledgers often separate three things:

1. what state an item is currently in,
2. what evidence or narrative explains that state,
3. what next action class is currently preferred.

When those three collapse, queues become readable only by local style familiarity. When they separate too aggressively, the archive overfits to a controller vocabulary larger than the work deserves.

## Working synthesis

DelayBasin should import only the smallest durable take:

- keep one compact `action_lane` family in `WITNESS-VOCABULARY.json`,
- use it only on durable queue or ledger items that already carry `discharge`,
- let the lane name the **primary next-step class**,
- keep exact evidence, branching detail, and local nuance in existing prose fields.

The admitted lane family is intentionally small:

- `promote`
- `replace`
- `retest`
- `rereview`
- `retire`
- `narrow`
- `keep-compact`
- `validate`
- `await-adjudication`

These are not a full controller ontology. They are a compact routing vocabulary for the next honest question: what class of move is this item mainly waiting for now?

## Action lane vs state token vs discharge prose vs broader code court

- **State token** says what posture the item is already in.
- **Action lane** says the primary next-step class.
- **Discharge prose** says the concrete condition, threshold, or branch logic for getting out of the current posture.
- **Broader code court** would classify many more issue kinds, reasons, and routing families than DelayBasin has currently earned.

So `action_lane` is not a replacement for state, not a compression of discharge prose, and not permission to import a larger queue-code or reason-code controller. It is a narrow bridge between stable status and explicit prose.

## Countermodels / probes

Possible failure modes are straightforward:

- the lane merely restates obvious discharge prose and adds no recoverable truth,
- the lane family grows too quickly and becomes a disguised code court,
- different ledgers start using the same lane token for incompatible action families,
- or later passes still cannot compare routing classes honestly even with the lane present.

Those are reasons to narrow, retire, or replace the family — not reasons to skip a bounded test entirely.

## Design consequences

When DelayBasin uses an action lane, each durable item should preserve:

- the **action lane / primary next-step class**,
- the **governed discharge surfaces / durable queues / ledgers** where that lane is used,
- the **comparability budget / how much surrounding prose can vary while the lane still stays comparable**,
- and the **narrow-lane / extend-registry / fail-closed-on-drift consequence** if the lane stops being honest.

This keeps the archive small while preventing repeated routing judgments from living only in remembered prose style.


## Derivative frontier cards

Once DelayBasin already keeps compact `action_lane` labels on durable items, a later careful pass may still need one smaller derivative card saying what current source-backed focus to inspect first.
That is where a tiny `frontier-ticket.json` can help.
It should stay derivative and source-backed: select one live focus from the already-admitted hot open-work slice, keep one tiny continuity background from the latest open obligation and latest cooling retrospective, and refuse to become a scheduler, dashboard, or queue court.

## Transformer-facing implication

If DelayBasin is partly acting as a bounded continuation substrate, then stable state alone is not always enough. Some of the operative continuation signal may live in which **class of next move** the archive currently licenses. A tiny action-lane family is a way to make that routing signal public without pretending DelayBasin has earned a full symbolic workflow controller.
