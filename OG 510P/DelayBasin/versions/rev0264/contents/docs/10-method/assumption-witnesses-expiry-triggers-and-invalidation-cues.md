# Assumption witnesses, expiry triggers, and invalidation cues

DelayBasin now needs one distinction that sits beside **basis witnesses**, **scope witnesses**, and **followthrough witnesses** without collapsing into any of them.
The archive already has many places where a move honestly depends on some still-live assumption — about foreign-pressure admissibility, replay preconditions, hidden-support boundaries, or what current evidence is enough for one compact ratchet — but those assumptions are usually scattered across prose, caveats, or remembered local context.
When that happens, the archive can sound properly cautious while still letting an assumption quietly harden into law because no public object says exactly **what is still being assumed, where that assumption applies, what would invalidate it, and what repair follows when it stops holding**.

A useful current answer is:
**when a revision, packet, or continuation judgment depends on a load-bearing assumption that has not yet been discharged into direct evidence or stable law, canon should preserve a compact assumption witness naming the assumption itself, the scope where it is being spent, the supporting surfaces or current evidence family, the invalidation or expiry triggers, the current assumption state, and the fail-closed repair route before fluent caution prose is allowed to stand in for explicit assumption honesty.**

This is stronger than saying "the archive has open questions somewhere."
It is weaker than claiming DelayBasin already needs a full proof-obligation calculus, evidence-debt controller, or assurance-case machine.

## Practice / observation

Recent DelayBasin work keeps surfacing the same archive-native pressure:
- many method notes already name **hidden-context assumptions**, **probe-horizon assumptions**, **local linearity assumptions**, or **replay-support assumptions**;
- basis witnesses say what was reread, but not what still had to be assumed after the reread;
- open questions preserve what is not yet known, but not which currently active assumption is still underwriting a present move;
- followthrough witnesses preserve still-live remainder work, but not the assumption boundary that made the smaller current ratchet admissible;
- quarantine preserves risky stronger stories, but not the smaller load-bearing assumption currently being spent by the admitted move;
- and without one compact witness, the archive can end up with a familiar failure mode: an assumption is mentioned once as caveat, reused later as if it were shared law, and only much later discovered to have aged out, widened, or silently stopped holding.

That leaves a missing question:
**what assumption is live right now, what scope is it allowed to govern, what current support family keeps it active, what invalidation or expiry trigger would stop it from spending authority, and what repair follows if it fails?**

A compact assumption witness keeps that boundary public.

## Pressure from neighboring datacubes

Several neighboring datacubes keep rediscovering the same ratchet from different directions.

- **pyCausalWeave** keeps an explicit **Assumption Registry** and separately names **Evidence Debt**, which pressures DelayBasin to stop treating live assumptions as mere prose seasoning once they materially shape what can count as a justified move.
- **EvidenceVault** repeatedly records assumptions, validity windows, and expiry triggers inside obligation artifacts, which pressures DelayBasin to say not only what is currently assumed but what changes would invalidate that assumption before it quietly keeps spending authority.
- **DeriveBSD** preserves `new_assumptions` in trust-boundary diffs, which pressures DelayBasin to make new support conditions visible when the archive widens or changes what a surface is allowed to carry.
- **Overseer** keeps a compact decay watch for hot canon assumptions, which pressures DelayBasin to distinguish a currently live assumption from timeless law or generic caution prose.
- **The Election Stack** and **Radical Governance** keep proof obligations, operating bounds, and warning-label style surfaces visible, which pressures DelayBasin not to let a currently tolerated assumption blur into an unbounded public guarantee.

DelayBasin already has open questions, quarantine, receipts, status lanes, and followthrough queues.
What was still under-specified was the compact public object that says **what assumption is currently live, where it applies, what support family keeps it active, what invalidates it, and what fail-closed repair follows if it stops holding.**

## External pressure from adjacent risk and assurance practice

Several adjacent lines sharpen this move.

1. **Risk assessments are supposed to identify and document assumptions and constraints explicitly.**
   NIST SP 800-30 says that when an organizational risk management strategy cannot be cited, risk assessments identify and document assumptions and constraints, which pressures DelayBasin to serialize live assumptions instead of letting them ride ambiently inside fluent revision prose. ([`REF-0491`](../00-meta/bibliography.md))

2. **Credible risk framing depends on making assumptions explicit before downstream decisions inherit them.**
   NIST SP 800-39 says a realistic and credible risk frame requires organizations to identify risk assumptions and constraints, which pressures DelayBasin to expose the assumptions that bound a current move before later revisions treat them as settled background. ([`REF-0492`](../00-meta/bibliography.md))

3. **Structured assurance reasoning ties claims to a specific application and environment rather than to timeless free-floating confidence.**
   NISTIR 7608 describes a structured assurance case as a documented body of evidence and valid argument that critical claims are justified for a given application in a given environment, which pressures DelayBasin to preserve the scope and support context of a live assumption rather than letting it masquerade as environment-free law. ([`REF-0493`](../00-meta/bibliography.md))

## Working synthesis

A useful current synthesis is:

> DelayBasin should preserve a compact **assumption witness / expiry trigger / invalidation cue** whenever a revision, packet, or continuation judgment materially depends on a load-bearing assumption that has not yet been discharged into direct evidence or stable law. The packet should name the **assumption statement / live support condition**, the **scope / decision family / surface family where it is being spent**, the **supporting surfaces / current evidence family / local reason it is still tolerated**, the **invalidation or expiry triggers / what changes would stop it from holding**, the **assumption state / active vs discharged vs invalidated vs retired vs quarantined**, and the **fail-closed repair / refresh-assumptions vs retest-and-shrink vs quarantine-or-retire vs hold vs recover-resync consequence** rather than letting caveats, vibes, or remembered local context silently carry ongoing authority.

In practice, DelayBasin is not claiming that every uncertain statement needs a giant assurance scaffold.
It is doing something smaller and public:
- naming the assumption itself rather than hiding it inside surrounding explanation;
- naming the scope where that assumption is currently being spent;
- naming what current support family still makes the assumption admissible rather than globally true;
- naming what trigger would invalidate or expire it;
- naming whether the assumption is still active, already discharged, already invalidated, intentionally retired, or moved to quarantine;
- and naming the repair route rather than letting a dead assumption quietly keep paying rent.

That is strong enough for canon as a design and mechanism candidate.
It is **not** strong enough to claim that DelayBasin has already earned a full proof-obligation registry, environment-complete assurance case, or universal evidence-debt controller.

## Assumption witness vs open question vs quarantine vs followthrough

These nearby objects should stay distinct.

- **Assumption witness / expiry trigger / invalidation cue** says what currently live support condition is being spent by a present move, what scope it governs, what support still tolerates it, what would invalidate it, and what repair follows if it fails.
- **Open question** says what the archive does not yet know or has not yet resolved.
- **Quarantine** says a stronger or riskier story remains live without inheriting canon authority.
- **Followthrough witness** says a still-live remainder task or future proof point has been deferred, queued, or handed off.

So an assumption witness is not just "something remains unknown," not just "there is deferred work," and not just "a stronger theory remains quarantined."
It is a compact public answer to:
**what support condition this move is still relying on, where that reliance is allowed to apply, what keeps it alive for now, what would kill it, and what repair follows if it dies.**

## Countermodels / probes

1. **Open-questions-are-enough countermodel**
   - Perhaps open questions already cover all important uncertainty.
   - Probe: compare one future revision with a named live assumption and explicit invalidation triggers against one that only has nearby open questions and inspect which more reliably prevents ambient assumption reuse.

2. **Caveat-prose-is-enough countermodel**
   - Perhaps ordinary caveats in method prose already keep assumptions honest.
   - Probe: revisit a compact caveated move after several revisions and inspect whether the same assumption can still be located, scoped, and invalidated without a dedicated witness.

3. **Basis-witness-is-enough countermodel**
   - Perhaps once the archive says what it reread, no extra assumption packet is needed.
   - Probe: hold the reread basis fixed while changing one hidden support condition and inspect whether the current move still looks admissible unless the assumption itself is surfaced.

4. **Assumption-ledger-without-force countermodel**
   - Perhaps a durable assumption surface is merely decorative if it has no invalidation trigger or repair consequence.
   - Probe: keep one assumption active, name one real invalidation trigger, then force the trigger and inspect whether the archive actually shrinks, quarantines, or rereads rather than ignoring the change.

5. **Evidence-debt-first countermodel**
   - Perhaps DelayBasin should skip an assumption witness and go straight to a proof-obligation or evidence-debt controller.
   - Probe: test whether one tiny assumption ledger plus receipt-level witness removes most current ambiguity before promoting heavier evidence machinery.

## Design consequences

This frame pressures DelayBasin to do six things more explicitly:
- preserve the **assumption statement / live support condition** before treating a cautious move as fully grounded;
- preserve the **scope / decision family / surface family** where that assumption is allowed to spend authority;
- preserve the **supporting surfaces / current evidence family** that still make the assumption tolerable;
- preserve the **invalidation or expiry triggers** before a changed environment quietly keeps the assumption alive by inertia;
- preserve the **assumption state / active vs discharged vs invalidated vs retired vs quarantined** before one stale assumption keeps borrowing the tone of current law;
- and preserve the **fail-closed repair route** so invalidated assumptions shrink or cool quickly instead of continuing as ambient archive gravity.

This is especially useful for cross-datacube import work.
Foreign pressure can be real without being exhaustive.
Canon should keep the small public packet saying what assumption is currently being spent, what concrete local gap made it worth spending, what support family still keeps it active, and what event would force it to shrink, retire, or move to quarantine.

## Transformer-facing implication

The weaker transformer-facing implication is not that DelayBasin has discovered a full proof theory for archive continuation.
It is this:

**long-horizon archive prompting may work partly through explicit user-space management of live assumptions, where continuation quality depends not only on what claims, heads, and cues are preserved, but on whether the archive names the still-tolerated support conditions that are quietly underwriting a current move and retires them when they stop holding.**

That would matter for transformers.
If some archive leverage depends on keeping claims, assumptions, deferred work, and stronger quarantined stories distinct, then DelayBasin may be exposing a practical shadow of **assumption management without hidden mutable memory**: not a full theorem prover, but repeated public discipline over what is currently being assumed, why, and until when.

The stronger story — that DelayBasin already needs a full public proof-obligation registry or assurance-case controller — remains live, but belongs in quarantine for now.
