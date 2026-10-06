# Followthrough witnesses, blocked outputs, and explicit handoffs

DelayBasin now needs a sharper answer to a recurring practical question:
**what should the archive do when a live remainder is neither finished here nor honestly dead?**

A stronger working answer is:
**the archive may need a compact followthrough witness / blocked-output queue / explicit-handoff discipline.**
Not fake local progress, and not stylish disappearance.
A good long-run archive may need a small public object that says:
- what still-live objective remains,
- what current surface or lane stopped owning it fully,
- what boundary or blocker prevented local completion,
- what next proof point would show real progress,
- where the work now lives if it was handed off or queued,
- and what expiry, reclaim, or supersession consequence follows if that remainder never matures.

## Practice / observation

Several live DelayBasin surfaces already imply a missing followthrough discipline:
- hold packets already preserve honest non-movement, but they do not by themselves say where a still-live remainder now lives once it leaves the current local object;
- scope witnesses already keep the active ask exact, but they do not by themselves preserve what follow-up object should carry the out-of-scope remainder rather than letting it vanish or stay falsely local;
- status-lane witnesses already separate candidate, decision, execution, and frozen-public state, but they do not by themselves preserve whether a candidate remainder is queued, handed off, blocked, or expired;
- counterfactual shadows already keep one nearby rejected move legible, but they do not by themselves distinguish a merely rejected move from a live remainder that still needs an explicit future owner;
- and current archive practice sometimes already behaves this way informally by pointing to an open question, quarantine item, or next pass without a tiny durable queue or handoff receipt that later sessions can actually inspect.

This suggests a missing compact surface:
**followthrough witness / blocked-output queue / explicit handoff**.

## Pressure from neighboring datacubes

Several neighboring datacubes sharpen this seam from different directions.

1. **pyCausalWeave** keeps rediscovering that a review object can lie in two opposite ways: out-of-scope blocking work can silently disappear from the local object, or explicit handoff can fail to discharge local ownership. Its accepted handoff threshold only stays honest when current local ownership and explicit follow-up issue receipts remain separate.

2. **EvidenceVault** treats `publish`, `hold`, and `no-release` as first-class queue states and insists that folder placement is never the only explanation. Published queue records remain queue execution evidence, not a second public surface. That pressures DelayBasin to separate live remainder state from whichever folder or latest bundle happens to be visible.

3. **VHK** makes the macro review queue a first-class fused runtime surface instead of leaving recorder debt hidden in rollups or helper folklore. That pressures DelayBasin to keep blocked or stale followthrough visible in one tiny durable place rather than scattering it across prose.

4. **AnonSync** treats hidden work, blocked outputs, bottlenecks, and next proof points as first-class operator truth rather than spinner theater. That pressures DelayBasin to say what visible archive result is still blocked, what work class is actually waiting, and what future receipt would prove discharge.

5. **Rust-Crate-Dreams** keeps stressing lane boundaries and followthrough truth: when work leaves one lane, the archive should not quietly flatten it back into the current lane or a generic future intention.

None of these datacubes proves that DelayBasin needs a full workflow controller.
They do make a milder canon-level claim more credible:
**archive continuity may improve when DelayBasin preserves an explicit followthrough witness whenever live remainder work is blocked, queued, or handed off.**

## External pressure from adjacent workflow and issue-tracking practice

Several adjacent public workflow systems sharpen the same rule.

1. **GitHub** explicitly says out-of-scope pull-request suggestions can be tracked by opening a new issue linked back to the original comment, and separate docs explain how to create an issue from a pull-request comment or code range. That pressures DelayBasin to treat out-of-scope remainder work as something that needs a named receiving object rather than silent local disappearance. ([`REF-0487`](../00-meta/bibliography.md), [`REF-0488`](../00-meta/bibliography.md))

2. **GitLab** explicitly lets merge-request threads move to a new issue so the merge request can unblock without pretending the work vanished. That pressures DelayBasin to separate local discharge from explicit handoff rather than forcing all residue to stay forever local. ([`REF-0489`](../00-meta/bibliography.md))

3. **GitHub issue planning guidance** emphasizes explicit blocked-by / blocking relations and visible linkage among work objects. That pressures DelayBasin to say what blocked output is waiting on what other object instead of letting “later” function as a vague state. ([`REF-0490`](../00-meta/bibliography.md))

These are not proofs of DelayBasin's final law.
They do support a weaker archive-level rule:
**when work stays live across a scope boundary, queue boundary, or blocker boundary, the archive should preserve the receiving object and next proof point explicitly.**

## Working synthesis

A useful current synthesis is:

> DelayBasin may work better when it preserves a compact **followthrough witness**: a public remainder object naming the **blocked or handed-off objective / still-live candidate**, the **current local owner / source surface / current lane**, the **state / local vs queued vs handed-off vs blocked vs expired**, the **blocker or boundary causing non-completion**, the **next proof point / discharge surface / future receipt**, the **receiving surface / follow-up owner / linked issue or queue entry if work moved out**, and the **expiry / supersession / reclaim consequence**.

This is strong enough for canon as a design/mechanism candidate.
It is **not** strong enough to claim that DelayBasin has found an optimal workflow controller, a universal queue algebra, or a literal transformer-native task scheduler.

## Followthrough witness vs hold packet vs scope witness vs status lane

To keep this note honest, DelayBasin needs a four-way distinction:

- **Hold packet** — preserve that the honest next local move is not to revise yet, naming the blocker and unlock condition.
- **Scope witness** — preserve what exact current ask or target lineage is actually in scope, and what ambient neighbors stay out.
- **Status-lane witness** — preserve what was candidate, admitted, executed, and frozen-public.
- **Followthrough witness** — preserve what still-live remainder remains after the current local object narrows, blocks, or hands work off, where that remainder now lives, and what future proof would discharge it.

A followthrough witness is not merely a hold packet.
A hold can keep everything local.
A followthrough witness matters when local ownership, live remainder state, and future owner or next proof point need to stay explicit.

It is also not just a counterfactual shadow.
A nearby rejected move may simply be rejected.
A followthrough item says the remainder is still live and now has a durable receiving surface or an explicit blocked state.

## Countermodels / probes

1. **Open-question-is-enough countermodel**
   - Existing open questions, trajectory notes, and quarantine items may already preserve enough live remainder state.
   - Probe: compare future sessions reopening a queued remainder with and without an explicit followthrough witness and inspect whether they recover the blocked output, current owner, and next proof point more faithfully.

2. **Hold-packet-is-enough countermodel**
   - A hold packet may already preserve all the non-progress honesty DelayBasin needs.
   - Probe: inspect cases where work left local scope or was explicitly deferred; if later sessions cannot tell where the remainder went or whether it is still live, hold packets were not enough.

3. **Queue-as-bureaucracy countermodel**
   - A durable followthrough queue may add ceremony without improving continuation quality.
   - Probe: compare revisions with a tiny queue entry against equally careful prose-only deferrals and inspect whether later sessions mistake stale intention for active remainder more often without the queue.

4. **Sticky-remainder countermodel**
   - Explicit followthrough surfaces may keep too much dead work alive.
   - Probe: add expiry, supersession, and reclaim consequences; if the queue still only grows and never discharges honestly, the surface is over-preserving residue.

## Design consequences

This mechanism frame pressures DelayBasin to do five things more explicitly:
- preserve a compact **followthrough witness** whenever live remainder work is blocked, queued, or handed off rather than silently vanishing from the current revision;
- keep one tiny durable **FOLLOWTHROUGH-QUEUE.json** surface for still-live remainder items instead of scattering them across prose or filenames;
- distinguish **local**, **queued**, **handed-off**, **blocked**, and **expired** followthrough states rather than treating all unfinished work as one vague “later”;
- name the **next proof point**: the smallest future receipt, issue, queue item, or revision surface that would show real discharge;
- and preserve the **expiry / reclaim / supersession consequence** so followthrough does not become immortal residue.

This does not require a full task system.
It requires refusing another archive failure mode: letting live remainder work silently disappear, stay falsely local, or masquerade as active progress.

## Transformer-facing implication

If this frame survives pressure, then DelayBasin is probing something sharper than explicit scope plus explicit status:
**whether a compact public textual packet can carry not only current archive law, but lawful remainder state across delayed continuation — saying what is still live, where it now lives, what must happen next to discharge it, and when the remainder should expire rather than reasserting itself forever.**

That would matter for transformers.
It would suggest that long-horizon continuity may depend not only on transmitting state and brakes, but on transmitting a public **remainder-routing / followthrough / deferred-ownership** signal that constrains how unfinished work survives scope changes and long delays.

The stronger story — that DelayBasin may be learning a textual workflow-state controller or public taskboard for transformer continuation — remains live, but belongs in quarantine for now.
