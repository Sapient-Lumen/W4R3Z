# 703 — Interface packets for lane-typed government stacks: lead lanes, handoffs, shared facts, escalation clocks, and no governance by glue folklore

## One-line thesis

Once the archive has split a composite field into lane-sized scope packets, it should also publish one **interface packet** for the resulting typed stack: name the lead for each lane, the handoff triggers between lanes, the shared facts and records that must travel, the timing and escalation rules, the fiscal and liability crosswalks, and the public route map, so distributed government does not collapse back into blame circulation, duplicate work, or quiet recentralization by whoever controls the glue.

## Why this matters

The archive now has a stronger sequence for ideal-government design.

- `699` gives the reusable scope spine.
- `700` gives the minimum design packet.
- `701` gives the adjudication matrix for genuine rival packets.
- `702` adds the bundle test and lane-splitting rule so composite fields are decomposed before rivalry begins.

But one compact piece was still missing. Once a field has been honestly split into several lanes, the polity still needs a way to govern **between** those lanes.

That missing piece matters because many multilevel failures do not begin with the wrong scope assignment. They begin with a tolerable assignment whose interfaces were never made constitutional. A municipal intake desk receives a case but does not know when specialist regional review is mandatory. A regional planning body can set corridor priorities but cannot force local record fields, so the network map and permit map diverge. A national rights-floor agency sets mandatory standards but leaves no typed route for local exceptions, so discretion returns through political calls or platform workarounds. A metro transport authority owns fares while municipalities own curbs and street permits, but neither side has a binding handoff clock when street works disrupt the network. In each case the lane split may be broadly right, yet the actual government still runs on custom, workarounds, and interoffice goodwill.

The archive therefore needs one more compression rule: **lane assignment is not enough**. A typed stack must also say how the lanes touch.

## Pattern pack

### 1. Treat the interface packet as a separate object from the lane packets

A lane-sized packet under `700` explains why one lane belongs at one scope. The **interface packet** is different. It explains how two or more already-assigned lanes interact without reopening the whole scope argument.

The archive should therefore keep the two objects distinct:

- the lane packet answers **who owns this lane and why**,
- the interface packet answers **how adjacent lanes exchange work, facts, money, clocks, and exceptions**.

This prevents every coordination problem from being misdiagnosed as proof that the underlying scope assignment was wrong.

### 2. Name one lead lane and one support lane for every consequential junction

At each real junction in a typed stack, the archive should identify:

- which lane is the **lead** for the decision in question,
- which lane is the **support** lane,
- what the support lane may require, advise, veto, or merely record,
- and when the lead changes because the issue has crossed a threshold.

This matters because many multilevel fields fail through **junction ambiguity** rather than through total absence of law. Several bodies are involved, but none can say who is currently in charge of this exact step.

### 3. Define handoff triggers by observable conditions, not by mood or prestige

A handoff rule should travel through observable conditions such as:

- a threshold risk score,
- a territorial spillover threshold,
- a rights-floor issue,
- a capital-cost threshold,
- a corridor or basin effect,
- a deadline overrun,
- or an emergency declaration.

The archive should reject handoffs triggered only by phrases like “where appropriate,” “for significant matters,” or “when higher-level coordination is needed,” unless those phrases are further typed into usable tests. Otherwise the stack quietly recentralizes toward the actor with the strongest staff, budget, or software.

### 4. Publish the shared-facts spine for every interface

Many lane disputes are really disputes about **which facts must be shared and in what form**.

The interface packet should therefore name the minimum shared-facts spine:

- the canonical identifiers,
- the event or case states that must travel,
- the required metadata,
- the authoritative system or record class,
- the update responsibility,
- the correction route,
- and the public disclosures that keep the handoff legible.

Without a shared-facts spine, a typed stack becomes one policy in speech and several incompatible governments in operation.

### 5. Put clocks on the junction, not only on the lane

A lane may have internal timeliness rules and still fail the public because the **junction** is ungoverned. The archive should therefore put clocks on the interface itself:

- referral deadlines,
- acknowledgement deadlines,
- decision-return deadlines,
- escalation deadlines,
- continuity duties when the receiving lane is unavailable,
- and timeout consequences.

This keeps a field from becoming publicly unusable at the seams even when each individual lane can claim it met its own internal standard.

### 6. Name the fiscal, staffing, and liability crosswalk at the seam

Interfaces are often where costs and blame disappear. One body refers. Another inspects. A third pays. A fourth inherits the complaint. The archive should therefore require a seam-level crosswalk naming:

- who pays for the handoff work,
- whether the receiving lane can bill, recover, or charge back,
- what staff or specialist capacity must be on call,
- who answers for delay or loss at the seam,
- and which authority carries liability for interim harm while a handoff is pending.

A typed stack without this crosswalk often looks decentralized in principle and adversarial in practice.

### 7. Separate ordinary handoff, urgent escalation, and temporary override

Not every upward movement in a stack is the same. The interface packet should therefore separate:

- **ordinary handoff** for routine adjacency,
- **urgent escalation** for time-critical situations,
- and **temporary override or fallback** for failure, incapacity, or emergency.

These are different constitutional events and should not share one vague clause. Otherwise every hard case becomes either informal commandeering or procedural paralysis.

### 8. Keep a public route map for people, places, and lower governments

The interface packet should not remain a backstage administrative memo. It should produce one visible route map that an outsider can use.

That route map should show:

- the normal front door,
- when another lane becomes mandatory,
- who must notify whom,
- where reasons and records appear,
- where complaints about the seam go,
- and what happens if the handoff breaks.

This is especially important where residents, firms, municipalities, or frontline agencies would otherwise have to solve the stack by jurisdiction hunting.

### 9. Audit seam stress, not only lane performance

A typed stack can show good lane-level performance and still fail through **seam stress**. The archive should therefore expect interface review to track questions such as:

- how often handoffs miss their clocks,
- how often facts are re-entered or contradicted,
- how often exceptions become routine,
- whether one lane is forced into unpaid support work,
- and whether emergency escalation is being used as ordinary governance.

This keeps interface design from becoming a one-time drafting exercise.

### 10. Prefer narrow stable interfaces over omnibus coordinators

When a stack needs glue, the archive should usually prefer a narrow stable interface packet over an omnivorous coordinator that slowly becomes the real government of the field.

The interface should be only as thick as necessary to move work, proof, money, and escalation across the seam. If the glue actor starts setting distributive priorities, territorial strategy, capital sequences, or binding standards across many lanes, the archive should ask whether this is no longer an interface at all but a new governing lane or an overdue constitutional upgrade.

## Compact interface packet

A normal-length interface object should usually fit in one table-like block:

| Field | Junction | Lead lane | Support lane | Trigger | Shared facts | Clock | Escalation | Public route |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| **Housing** | homelessness intake → specialist housing/health review | municipal intake lane | regional specialist-review lane | repeated safeguarding flag, severe complexity, or statutory threshold | case ID, risk flags, prior placements, duty status | referral within fixed hours or days | emergency welfare escalation or temporary fallback duty | resident sees one intake path and one review status path |
| **Transport** | municipal street works → metropolitan network co-ordination | municipal street-authority lane | metro network lane | corridor disruption, service diversion, or threshold ridership effect | permit ID, dates, closure geometry, service map impact | notify before works; real-time updates during disruption | central operations cell if corridor integrity fails | traveler sees one disruption notice and one accountable coordinator |
| **Water** | local inspection → basin or national pollution enforcement | local witnessing/inspection lane | basin or national enforcement lane | transboundary discharge, repeat breach, or protected-source risk | site ID, samples, notices, chain of custody | referral and acknowledgment within fixed clock | emergency powers for acute contamination | public sees one complaint path and one enforcement-status lane |

The archive should treat this as the normal length unless the seam is unusually hard.

## Guardrails

- Do not treat every coordination problem as proof that the scope assignment was wrong.
- Do not leave lead/support roles implicit at consequential junctions.
- Do not use soft phrases like “where appropriate” in place of observable handoff triggers.
- Do not govern shared facts by custom, spreadsheet relay, or email folklore.
- Do not let urgent escalation silently become the ordinary constitutional route.
- Do not create a glue body so thick that it is really an unacknowledged new tier.

## Failure modes

- **glue folklore** — the stack runs on habit, relationships, and remembered favors rather than on a declared interface packet.
- **junction ambiguity** — several bodies touch the same seam, but none can say who currently leads.
- **trigger vagueness** — handoff rules exist only as prestige phrases that invite quiet centralization or buck-passing.
- **shared-fact fracture** — adjacent lanes depend on incompatible identifiers, states, or update duties.
- **seam delay laundering** — each lane claims compliance while the user is stranded in the transfer gap.
- **override creep** — emergency or fallback rules become the everyday way the field is really governed.
- **coordinator inflation** — a body created to move work across lanes slowly becomes the hidden owner of the field.

## Practical tests

A typed stack is using interface packets honestly when it can answer yes to all of the following:

1. Has the archive kept lane assignment and seam design as distinct objects?
2. Is there a named lead and support lane for each consequential junction?
3. Are handoff triggers observable enough that outsiders could tell when the lead changes?
4. Is there a minimum shared-facts spine and correction route for the seam?
5. Do the clocks, liability rules, and escalation paths attach to the junction itself?
6. Could a resident, firm, municipality, or frontline worker follow one public route map without solving the stack by folklore?

## Compression rule for the archive

If a later note presents a **lane-typed stack** but cannot say **who leads at each seam, what facts and clocks travel across the seam, how escalation works, and where the public goes when the handoff breaks**, then it still has **scope decomposition without an interface constitution**, and its distributed design is not yet governable.
