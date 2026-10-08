# Split-lane packet display and dependency rules

This document closes the archive's next live gap about **how one learner-facing continuity packet may display several live lanes without making staggered clocks look like one synchronized schedule**.

[`no-fault-transition-cost-absorption-and-fee-waiver-rules.md`](no-fault-transition-cost-absorption-and-fee-waiver-rules.md) already gives the archive:

- the escalation packet shell (`NS1-NS8`, `EV1-EV6`, `OW1-OW3`, `TM1-TM3`, `NW1-NW4`);
- the cohort / supplement / refresh grammar (`CG0-CG3`, `IS1-IS5`, `RF1-RF5`);
- unresolved-field marking (`UF0-UF4`, `MK1-MK6`, `GU1-GU4`);
- learner-action / pause rules (`PA0-PA4`, `PC0-PC4`);
- restart fairness (`RN1-RN4`, `GR0-GR3`, `RM0-RM3`);
- and restart synchrony (`SY0-SY3`).

What it still lacked was the next narrower answer:

> **when route, money, support, and external-rights lanes may still be shown together inside one packet, what dependency / precedence / owner fields must stay visible, and when one later lane must instead move into a clearly separate supplement or packet so a learner does not mistake "later" for "shorter".**

The archive's tighter answer is:

> **one packet may carry several lanes only if each lane stays visibly lane-scoped, owner-scoped, and trigger-scoped; convenience is never enough to collapse split clocks into one apparent schedule.**

Current public signals point the same way. OECD's 2025 Education Policy Outlook says lifelong-learning systems need to move beyond fragmented initiatives and support non-linear transitions. ACE's current learner guidance says transfer-credit policies carry their own documentation requirements and deadlines. Federal Student Aid now says FAFSA Submission Summary aid figures are estimates while school aid offers are the final determination, and it separately requires schools to obtain transfer-student aid history before disbursing aid. OIA's current Completion of Procedures guidance still expects the final internal letter to state the decision, reasons, and deadline, and to flag cases where time-critical remedies may become impossible later. These are all signals that route, money, and complaint / rights lanes often mature on different owners and different events even when the learner experiences them as one disruption. See `B177`, `B180`, and `B181`.

## Relationship to the existing packet stack

This document does **not** replace:

- [`portable-public-learning-packet-and-recognition-profile.md`](portable-public-learning-packet-and-recognition-profile.md)
- [`no-fault-transition-cost-absorption-and-fee-waiver-rules.md`](no-fault-transition-cost-absorption-and-fee-waiver-rules.md)

Those documents answer:

- what claims and recognition defaults may travel across public learning routes;
- when continuity, money, support, complaint, regulator, or debt-relief lanes become live;
- when fields may stay cohort-wide, must split, may remain unresolved, may support reversible learner action, and may restart.

This document now answers a different question:

- **how those already-live lanes may be co-displayed without false synchrony, false sequencing, or buried rights.**

## Core rule

The archive now treats **split-lane packet display** as a separate layer on top of restart synchrony.

### Rule 1. One packet is allowed only with visible lane boundaries

If more than one lane is shown together, the learner-facing packet must preserve a visible row, card, or subsection for each lane. A packet may not rely on one undifferentiated deadline list once `SY0`, `SY2`, or `SY3` is doing real work.

### Rule 2. Every displayed lane must publish its operative anchor

A lane may not show only a date. It must show **what event made that date operative**: refreshed route offer, actual aid posting, actual disbursement, final internal decision, Completion of Procedures Letter, regulator acceptance, discharge notice, individualized supplement, or equivalent.

### Rule 3. Dependency is a field, not an inference

If one lane waits on another owner, event, or individualized supplement, the packet must say so explicitly. It is not enough to place a later row lower on the page and hope the learner infers the dependency.

### Rule 4. One live lane does not silently waive another

Where more than one remedy lane remains live, the packet must make non-waiver visible. Accepting a route hold, reading a settlement figure, or using one internal review path should not silently look like the learner has forfeited refund, complaint, regulator, or debt-relief routes unless the system can truthfully say so and names the lawful basis.

## The four display postures the archive now distinguishes (`DL0-DL3`)

| Display posture | Meaning | When it is the archive's default | What it forbids |
|---|---|---|---|
| `DL0 single-lane display` | the packet may use one common schedule block because only one lane is live or all displayed lanes satisfy `SY1` and truly share one operative anchor | one refreshed packet makes all displayed lanes decision-ready on the same clarified facts and no displayed lane awaits a later owner act or individualized supplement | using `DL0` merely because the institution wants one neat notice |
| `DL1 shared packet with split lane rows` | one packet may carry several lanes, but each lane gets its own row/card with its own owner, state, anchor, and consequence | several lanes are already worth showing together, but at least one lane uses `SY0` or `SY2` and therefore has a different operative date or owner | one page that still looks like one synchronized countdown |
| `DL2 cohort core plus lane supplement` | the packet may publish a common core plus a clearly separate supplement for one or more lanes | a common disruption fact is shared, but a later lane depends on a learner-specific route set, individualized money figure, individualized rights trigger, or later owner output | letting a cohort-core date silently govern a later individualized lane |
| `DL3 separate packet or protected channel` | a lane should leave the shared packet entirely and travel in its own notice/channel | the lane has a different protected audience, materially different evidence packet, a different access / adjustment channel, or enough legal / practical independence that co-display would bury or confuse it | hiding a rights-critical or privacy-critical lane inside a convenience bundle |

The archive's anti-slippage rule is now explicit:

> **co-display is a presentation privilege earned by truthful common context, not a license to collapse split lanes back into one apparent procedure.**

## Minimum lane-display fields that now travel (`LD1-LD7`)

If a lane appears anywhere inside a shared packet or supplement, the archive now says seven display fields must be visible.

| Field | What must be shown | Why it is now required |
|---|---|---|
| `LD1 lane label` | route / placement, money / aid / charges, support, complaint / review, regulator, debt-relief / discharge, or equivalent | the learner must see that several lanes exist, not one amorphous problem state |
| `LD2 current lane state` | paused, running, estimate only, awaiting owner act, awaiting learner supplement, final internal decision reached, externally filed, closed, or equivalent | state tells the learner whether the lane is already decision-ready or still maturing |
| `LD3 operative anchor` | the date plus the event that made it operative | a bare date invites false synchrony and false finality |
| `LD4 owner and contact route` | named office / role and where to act or ask | owner blur is one of the main reasons later lanes vanish in practice |
| `LD5 dependency / awaits field` | what this lane still depends on, or `none` | dependency must be published rather than inferred from layout |
| `LD6 learner action and consequence` | what the learner may do now, what remains optional, and what consequence follows if the lane expires | a visible lane that still hides the action/consequence is not yet an honest lane |
| `LD7 non-waiver / coexistence statement` | whether acting on this lane leaves other lanes live, pauses them, or lawfully affects them | co-displayed lanes otherwise look mutually exclusive by default |

These fields are intentionally lighter than the full escalation packet. They are the **display minimum**, not the whole case file.

## The four precedence relations the archive now distinguishes (`PX0-PX3`)

The packet should not imply one universal order. It should publish the narrowest truthful relation between lanes.

| Precedence code | Meaning | Typical fit |
|---|---|---|
| `PX0 independent-parallel` | the lane may run on its own timetable without waiting for another displayed lane | route selection and complaint preparation may both be live |
| `PX1 recommended-first` | one lane is practically sensible to use first, but it is not a legal or operational prerequisite and the later lane stays preserved | the institution recommends route stabilization before final refund calculation |
| `PX2 hard dependency` | the later lane cannot become decision-ready until a named owner act, posting, or final internal / external event occurs | money lane awaits actual aid posting; external complaint lane awaits final internal decision / COP Letter |
| `PX3 parallel-but-nonwaiving` | more than one lane is live and the packet must say explicitly that using one does not surrender the others | accepting a temporary place hold does not waive refund, complaint, or discharge guidance |

A packet may show more than one `PX*` relation across different lane pairs. The point is not elegance. The point is honesty.

## When a lane must move from shared packet to supplement or separate packet

### Move to `DL2` when any of these becomes true

1. **learner-specific route set** — the route lane now depends on a learner-specific equivalent-option set, host availability set, or individualized protected-band rebuild;
2. **individualized money state** — actual charge, aid, refund, or compensation facts now differ materially across learners;
3. **individualized rights trigger** — only some learners have reached a final internal decision, regulator acceptance, discharge-eligibility posture, or similar trigger;
4. **individualized access / adjustment need** — a lane now requires a different accessible format, translation, or protected delivery route than the cohort core.

### Move to `DL3` when any of these becomes true

1. **protected channel requirement** — the lane contains protected support or case facts that should not travel in the shared packet;
2. **evidence-packet divergence** — the lane now depends on a materially different evidence bundle or a different owner / review regime;
3. **independent rights lane** — the lane is sufficiently separate that co-display would make it look like a mere appendix to the owner-preferred remedy;
4. **cross-owner burden** — the lane sits with a genuinely different office family and would be missed or misrouted if left in a convenience bundle.

## What the packet may still keep in a common core

Even after split-lane display hardens, a cohort core may still carry:

- the common disruption event;
- the common explanation of what changed;
- shared evidence-collection instructions;
- the list of lane types that may later appear;
- and a high-level non-waiver statement saying that later individualized lanes may remain live.

But the cohort core may not pretend it already knows:

- the final route set for each learner;
- the actual money state for each learner;
- the exact owner or deadline for a not-yet-triggered rights lane;
- or whether one lane is mandatory before another unless that dependency is already true.

## Starter examples

### Example 1. Route lane live now; money lane still pending

A provider has already reopened route continuity and offered a protected transfer or teach-out option, but the exact refund / aid figure still depends on actual posting or disbursement records.

Archive default:

- use `DL1`;
- show route and money as separate rows;
- mark the relation as `PX1` or `PX2` depending on whether the money lane is merely recommended-later or actually cannot mature yet;
- publish `LD3-LD7` for both rows.

### Example 2. Cohort closure notice plus individualized external-rights timing

A whole cohort receives the same closure event, but only some learners have reached the final internal step that activates an external complaint or discharge clock.

Archive default:

- use `DL2`;
- keep the closure facts and shared help routes in the cohort core;
- move the complaint / discharge lane into a learner-specific supplement when it actually becomes live.

### Example 3. Shared packet would bury a protected support lane

The route and complaint lanes are public enough to sit in one packet, but the learner also needs a protected support or accessibility lane that requires narrower disclosure.

Archive default:

- use `DL3` for the protected support lane;
- keep only the existence of a protected route visible in the shared packet;
- move the operative support details into the protected channel.

## Failure modes the archive is now trying to stop

1. **late-is-shorter failure** — a later lane is shown under an earlier one without a separate anchor, so it looks like a shorter or secondary version of the first lane.
2. **false-prerequisite failure** — the packet layout makes a recommended-first lane look mandatory.
3. **rights-burial failure** — complaint, regulator, or discharge lanes are technically mentioned but visually subordinated to the owner-preferred remedy.
4. **owner-blur failure** — the learner sees the lane but still cannot tell which office owns it.
5. **backdated-supplement failure** — an individualized lane becomes real later, but the deadline is still measured from the earlier shared packet.

## Current archive bet

The archive's current best guess is that a **small lane-display layer (`DL0-DL3`) plus a seven-field display minimum (`LD1-LD7`) plus a narrow precedence grammar (`PX0-PX3`)** will outperform both extremes:

- one giant multi-lane packet that buries different owners, triggers, and deadlines inside an apparently tidy single schedule;
- and full packet fragmentation where every lane disappears into a different office notice before the learner can see the shape of the problem.

That claim is now canon, but still live. The archive now sharpens it with a tiny sector-and-function starter profile layer so higher-ed teach-out, workforce / adult-route continuity, library / civic handoff, licensure-sensitive routes, and protected support channels no longer inherit one generic starting posture; see [`../20-governance/sector-and-function-profile-splits-for-split-lane-display-defaults.md`](../20-governance/sector-and-function-profile-splits-for-split-lane-display-defaults.md). It now adds one still narrower branch / retreat layer too, so inherited display profiles split further when after-hours posture, office family, or external-owner timing diverges and retreat entirely when protected or urgent lanes would be miscast as one ordinary office queue; see [`../20-governance/branching-and-retreat-rules-for-split-lane-display-profiles.md`](../20-governance/branching-and-retreat-rules-for-split-lane-display-profiles.md). And it now adds one final after-hours service-truth layer (`TV0-TV4`, `AY0-AY4`, `AN0-AN4`) so a visible child branch must say whether it is merely informational, receipt-only, queue-preserving, or genuinely live; see [`../20-governance/availability-acknowledgement-and-action-now-fields-for-after-hours-split-lane-branches.md`](../20-governance/availability-acknowledgement-and-action-now-fields-for-after-hours-split-lane-branches.md). The next narrower question is no longer what an after-hours child branch must minimally say, but **which of those service-truth defaults can harden across sector profiles and when queue-preserving or rights-preserving intake must split further by stakes, office family, or protected support type.**
