# Basis witnesses, expected-head guards, and session-honesty bridges

DelayBasin now needs a sharper distinction than **innovation packets**, **revision receipts**, or **operational-head registers** alone.
A revision can be locally coherent, grounded in a real anchor, and still silently inherit authority from the wrong basis: a stale head, a partial reread, a copied summary, or same-session glow that never proved the archive could actually recover the decisive state.
When that distinction stays implicit, the archive quietly treats “I can continue from here now” as if it already meant “this move was honestly grounded in the current archive basis.”

A useful current answer is:
**when a revision, replay verdict, review judgment, or canon move is being treated as grounded in current archive state, canon should preserve a compact basis witness naming the expected head, the actually reread basis, the session-provenance posture, the basis-state classification, and the fail-closed repair route before any stale or partial basis is allowed to inherit decision authority.**

This is stronger than saying “the receipt names the previous revision.”
It is weaker than claiming DelayBasin has already discovered a full compare-and-set continuation controller or universal optimistic-concurrency law for archive evolution.

## Practice / observation

Recent DelayBasin work keeps surfacing a recurring ambiguity:
- innovation packets already name an anchor revision, but the archive still rarely says whether the current move was actually grounded in that anchor or merely adjacent to it in the present session;
- operational-head registers now separate live heads from frozen citation heads, but the archive still rarely says whether a revision reread the live head it claims to extend;
- sufficiency and sham-runtime probes test whether reduced packets can reopen the right regime, but the archive still rarely records whether the present revision relied on explicit reread, copied summary, or same-session carry;
- a session can preserve reviewer-like or watcher-like awareness of some surface without preserving an active current basis for judgment;
- some revisions look justified because the right docs were “around,” even when the decisive move was actually inherited from local glow, not from a named reread basis;
- and some stale or mismatched basis states should clearly fail closed to reread, rerequest, hold, or `recover-resync`, but the archive still rarely says that explicitly.

That leaves a missing question:
**what exact basis was expected, what exact basis was actually reread, how much same-session carry remained in play, what basis state currently applies, and what repair route follows if the move was grounded on the wrong head or an under-specified basis?**

A compact basis witness keeps that boundary public.

## Pressure from neighboring datacubes

Several neighboring datacubes keep rediscovering the same discipline from different directions.

- Some distinguish **reviewer roster presence** from **current active request**, which pressures DelayBasin to keep “the surface is known” separate from “the current judgment is grounded on the current head.”
- Some insist that merge, queue, or approval actions stay scoped to an **expected head**, which pressures DelayBasin not to let a move silently rebind from one reviewed state to another.
- Some distinguish **native session identity** from **replayed or copied report views**, which pressures DelayBasin to say whether a present conclusion came from explicit reread, replay, copy, or local session adjacency.
- Some insist on **exact scope** and **fail-closed exposure posture**, which pressures DelayBasin to classify basis state sharply rather than speaking in flattering but under-specified continuation prose.
- Some distinguish **transient status glow** from **durable outcome visibility** and keep drift details in named witnesses, which pressures DelayBasin to make basis drift a compact named packet rather than something hidden inside generic revision fluency.

DelayBasin already has receipts, hold packets, innovation packets, self-sufficiency probes, and operational-head registers.
What was still under-specified was the compact public object that says **what basis was expected, what basis was actually used, how session-local the grounding still was, and what fail-closed repair follows if the basis is wrong.**

## External pressure from adjacent update and provenance practice

Several adjacent lines sharpen this move.

1. **Conditional update semantics increasingly require comparing an expected validator against the current state before mutation.**
   RFC 9110 defines `If-Match` as a precondition that is evaluated before the method is performed, so state-changing requests can fail rather than silently applying to the wrong current representation. That pressures DelayBasin to prefer explicit expected-head guards over silent stale-basis inheritance. ([`REF-0474`](../00-meta/bibliography.md))

2. **Modern collaboration APIs expose expected-head fields rather than treating merge intent as an unscoped toggle.**
   GitHub's GraphQL input objects include `expectedHeadOid` for merge-related mutations. That pressures DelayBasin to preserve when a continuation judgment or archive move was scoped to one reviewed head rather than pretending all later heads are equivalent. ([`REF-0475`](../00-meta/bibliography.md))

3. **Fresh-session review can outperform same-session review even when the final artifact stays fixed.**
   Cross-Context Review reports that separating production and review sessions improves output quality relative to same-session review, which pressures DelayBasin to keep session-honesty explicit rather than treating local adjacency as neutral. ([`REF-0223`](../00-meta/bibliography.md))

## Working synthesis

A useful current synthesis is:

> DelayBasin should preserve a compact **basis witness / expected-head guard / session-honesty bridge** whenever a revision, replay verdict, review judgment, or canon move is being treated as grounded in current archive state. The packet should name the **judged move / continuation claim / active decision surface**, the **expected basis / anchor revision / reviewed head**, the **actual reread basis / loaded surfaces / observed head**, the **session provenance / explicit reread vs copied summary vs nearby-session carry posture**, the **basis state / current vs stale vs partial vs mismatched vs resynced**, and the **fail-closed repair / bounded reread vs rerequest vs hold vs recover-resync consequence** rather than letting stale basis, partial reread, or session glow silently inherit decision authority.

In practice, DelayBasin is not claiming that every revision needs a giant concurrency protocol.
It is doing something smaller and public:
- naming the exact decision or judgment whose grounding matters rather than gesturing at “the revision” in general;
- naming the expected anchor revision or head rather than assuming the current basis was obvious;
- naming the actually reread basis or saying explicitly that the current move is only partially grounded;
- naming whether the present judgment came from explicit reread, copied packet, replayed summary, or same-session proximity;
- naming the current basis-state classification rather than describing confidence in vague prose;
- and naming the fail-closed repair route rather than silently absorbing a stale basis into ordinary continuation.

That is strong enough for canon as a design and mechanism candidate.
It is **not** strong enough to claim that DelayBasin has isolated a full compare-and-set state machine, perfect session-separation law, or universal concurrency protocol for archive evolution.

## Basis witness vs innovation packet vs operational-head register vs revision receipt

These nearby objects should stay distinct.

- **Basis witness / expected-head guard / session-honesty bridge** says whether a present move was honestly grounded on the head or basis it claims to extend.
- **Innovation packet** says what local delta should transmit against a shared anchor state.
- **Operational-head register** says which head is live and which head is frozen enough to cite for a named surface lineage.
- **Revision receipt** says what transition occurred and what checks made it admissible.

So a basis witness is not just “the revision had an anchor,” and not just “this head is live.”
It is a compact public answer to:
**what basis this move expected, what basis it actually used, how much current-session carry still mattered, and what repair follows if the basis was wrong.**

## Countermodels / probes

1. **Anchor-is-enough countermodel**
   - Naming a previous revision in the receipt may already look like enough basis discipline.
   - Probe: require an explicit expected basis plus observed basis and see whether stale-head or partial-reread cases still disappear into fluent continuation.

2. **Same-session-neutrality countermodel**
   - Same-session adjacency may not distort judgment in any practically important way.
   - Probe: compare one move justified after explicit reread with one justified from nearby session memory only, then inspect whether the archive preserves the same decision under cold reopen or review separation.

3. **Silent-rebind countermodel**
   - A later head may often be close enough that reusing an earlier judgment causes no real harm.
   - Probe: preserve one expected-head guard and test whether stale-head mismatch should route to reread, rerequest, or ordinary continuation.

4. **Basis-ceremony countermodel**
   - DelayBasin may be adding a ritual packet that duplicates innovation anchors, receipts, and operational-head registers without practical leverage.
   - Probe: keep the packet tiny and demand one real consequence when basis state is stale, partial, or mismatched.

5. **Hidden-support countermodel**
   - The move may only look grounded because the surrounding current session still carries decisive cues that the named basis alone would not restore.
   - Probe: pair one basis witness with one bounded reread or cold-open replay and inspect whether the move survives when session-local adjacency is reduced.

## Design consequences

This frame pressures DelayBasin to do six things more explicitly:
- preserve the **judged move / continuation claim / active decision surface** before talking about basis honesty at all;
- preserve the **expected basis / anchor revision / reviewed head** before letting a later head inherit the judgment;
- preserve the **actual reread basis / loaded surfaces / observed head** before claiming the move was grounded on current archive state;
- preserve the **session provenance / explicit reread vs copied summary vs nearby-session carry posture** before treating a fluent local continuation as an honest cold-open result;
- preserve the **basis state / current vs stale vs partial vs mismatched vs resynced** before letting under-specified confidence harden into canon;
- and preserve the **fail-closed repair / bounded reread vs rerequest vs hold vs recover-resync consequence** so stale basis loses authority quickly instead of silently rebinding.

This is especially useful during fast revision runs.
GPUstorming can still discover real local syntheses.
Canon should keep only the small public packet saying what head the move expected, what head it actually used, how much session-local carry remained, and what happens if that grounding proves stale.

## Transformer-facing implication

The weaker transformer-facing implication is not that DelayBasin has found a full concurrency controller.
It is this:

**long-horizon archive prompting may work partly through explicit user-space basis discipline over textual control surfaces, where continuation quality depends not only on what packets exist or what head is live, but on whether the current move was actually grounded through reread on the head it claims to extend.**

That would matter for transformers.
If some archive leverage depends on separating **live state**, **frozen reference state**, and **honestly reread current basis**, then DelayBasin may be exposing a practical shadow of **conditional update semantics without weight updates**: not a full transactional system, but repeated public compare-and-repair discipline over textual continuation heads.

The stronger story — that DelayBasin is already learning a real compare-and-set continuation controller or session-separation law over archive evolution — remains live, but belongs in quarantine for now.
