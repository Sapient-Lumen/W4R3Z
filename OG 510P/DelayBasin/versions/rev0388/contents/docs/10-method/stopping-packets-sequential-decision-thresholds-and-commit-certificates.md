# Stopping packets, sequential decision thresholds, and commit certificates

DelayBasin now has better language for
- what ambiguity class is live,
- which probe might separate it,
- how a fresh session can re-orient,
- and which cheap probe should probably go first.

That still leaves a bounded-state hole:
**when is there enough evidence to stop probing and commit to the next continuation move?**

A useful working answer is:
**preserve a compact stopping packet whenever the archive is using sequential probing or staged ambiguity reduction, and make the commit threshold public.**
That packet should name:
- the live ambiguity class,
- the decision threshold or commit criterion,
- the continuation action licensed if the threshold is crossed,
- the tolerated error / rollback posture,
- and the fallback if budget is exhausted before the threshold is met.

This is stronger than merely saying “we should probably stop soon.”
It is weaker than claiming DelayBasin has already discovered a literal sequential test, optimal stopping boundary, or public Wald-like decision rule over continuation space.

## Practice / observation

Several existing DelayBasin surfaces already pressure this move:
- identification packets say what observation would separate rival continuation hypotheses, but not yet what counts as *enough* separation to act;
- homing packets preserve orientation policy under ambiguity, but not yet the public commit point at which the archive should stop spending bounded state on re-orientation;
- probe-economics packets say which cheap probe should go first, but not yet when the probing campaign should end rather than continue nibbling at uncertainty;
- hold packets serialize honest non-movement, but they do not by themselves say when fresh evidence should discharge the hold;
- intervention-equivalence and causal-control packets say which distinctions still matter for action, but not yet what confidence, witness, or branch separation is sufficient to choose that action publicly.

Without a compact stop-rule surface, DelayBasin risks two opposite failures:
- **premature commit theater**, where one locally satisfying probe result gets rhetorically upgraded into enough evidence without a public threshold;
- **endless inquiry theater**, where the archive keeps buying more probes because no explicit condition ever says the current ambiguity has been reduced enough to move.

## Mechanism pressure from outside the archive

Several outside lines of work sharpen this move.

1. **Sequential tests are not just about what to sample, but when to stop and decide.**
   Modern presentations of Wald-style sequential testing still treat the object as a pair: a stopping rule plus a decision rule. That pressures DelayBasin away from preserving only probes or packet state while leaving the stop condition implicit in prose mood. ([`REF-0190`](../00-meta/bibliography.md))

2. **Active sequential hypothesis testing couples action choice and stopping choice.**
   Naghshvar and Javidi frame the decision maker as dynamically collecting observations while accounting for wrong-declaration cost, using the current information state to select informative sensing actions. That pressures DelayBasin to treat “stop now versus buy one more probe” as part of the same object as ambiguity handling, not a separate literary flourish. ([`REF-0191`](../00-meta/bibliography.md))

3. **Optimal stopping in sequential experimental design is explicitly a continuation-versus-terminal-value comparison.**
   Cheng and Huan show that threshold rules can be myopic and formulate stopping jointly with design policy, where stopping is optimal when terminal reward outweighs expected continuation value. DelayBasin should not import that whole formalism into canon, but the weaker pressure is strong: a bounded public stop rule should compare the value of moving now against the value of one more probe, not simply inherit the local appetite for continued inquiry. ([`REF-0192`](../00-meta/bibliography.md))

4. **Practical sequential tests can look deceptively precise while still misusing thresholds.**
   Fischer and Ramdas show that approximate SPRT thresholds are widely used in practice even when they fail to guarantee desired error control or sample optimality. That is direct pressure against DelayBasin turning “threshold” language into prestige theater: if the archive names a decision threshold, it should also name what kind of error / rollback posture that threshold is actually supposed to control. ([`REF-0193`](../00-meta/bibliography.md))

5. **Finite attention budget makes stopping part of context economics.**
   Anthropic's context-engineering note treats context as a finite resource with diminishing returns. DelayBasin therefore should not preserve sequential probe plans without also preserving the compact public reason they should stop before bounded-state and token budget are slowly eaten by low-yield refinement. ([`REF-0167`](../00-meta/bibliography.md))

## Working synthesis

A useful current synthesis is:

> DelayBasin should preserve **stopping packets / sequential decision thresholds / commit certificates** whenever ambiguity is being reduced by staged probes rather than one-shot evidence. The packet should say when the archive is allowed to stop probing and advance, what action that licenses, how much residual error or rollback risk is being tolerated, and what happens if the budget runs out first.

In practice, DelayBasin is not fitting exact likelihood-ratio boundaries.
It is doing something smaller and public:
- naming the ambiguity class,
- naming the decision threshold or commit criterion,
- naming the continuation action licensed by threshold crossing,
- naming the tolerated error / rollback posture,
- and naming the budget-exhaustion fallback (`hold`, `recover-resync`, bounded rollback, or escalate to a deeper probe family).

That is strong enough for canon as a bounded anti-drift discipline.
It is **not** strong enough to claim that DelayBasin has already discovered a literal sequential test, Bayes-optimal stopping boundary, or public optimal-stopping controller over continuation space.

## Probe-economics packet vs stopping packet

To keep this note honest, DelayBasin now needs a live distinction:

- **Probe-economics packet** — says why this candidate probe family should go first under bounded budget.
- **Stopping packet / sequential decision threshold / commit certificate** — says when the archive should stop buying further probes, what continuation action becomes legitimate, and what fallback applies if the threshold is not reached before the budget is gone.

These are related but not identical.
A probe-economics packet can justify the first cheap probe without saying when to stop the campaign.
A stopping packet can justify commitment after several probes without saying which one deserved to be purchased first.
DelayBasin needs both whenever ambiguity resolution is genuinely sequential rather than one-shot.

## Countermodels / probes

1. **Narrative-confidence countermodel**
   - The archive may simply be stopping when the prose feels confident enough.
   - Probe: require an explicit decision threshold or commit criterion plus the continuation action it gates.

2. **Threshold-prestige countermodel**
   - “Threshold” language may import statistical seriousness without any real control over residual error or rollback posture.
   - Probe: require an explicit tolerated error / rollback posture and a budget-exhaustion fallback; otherwise keep the move below canon.

3. **Never-stop countermodel**
   - Ambiguity may always admit one more plausible probe, so sequential discipline may expand into inquiry theater.
   - Probe: require that a stopping packet compare at least implicitly the value of moving now versus the next deferred probe.

4. **Stop-too-early countermodel**
   - Compact stop rules may encourage premature canonization from one aesthetically satisfying witness.
   - Probe: preserve the first failure signature or rollback trigger that would show the stop threshold was too lax.

5. **Ordinary planning countermodel**
   - The useful work may come from common-sense planning and web research, with explicit stopping packets adding little.
   - Probe: compare ambiguous revisions with and without an explicit commit threshold and check whether the packet actually reduces repeated uncertainty or ritual extra probing.

## Design consequences

This frame pressures DelayBasin to do five things more explicitly:
- when probing sequentially, name **what ambiguity class** is being reduced;
- preserve a **decision threshold or commit criterion** rather than letting “enough evidence” stay aesthetic;
- preserve the **continuation action** licensed if the threshold is crossed;
- preserve a compact **error / rollback posture** so stop language does not masquerade as certainty;
- and preserve a **budget-exhaustion fallback** so the archive has a public exit when the threshold is not reached in time.

A minimal stopping packet can stay very small:
- one ambiguity class,
- one threshold or commit criterion,
- one licensed continuation action,
- one error / rollback posture,
- and one budget-exhaustion fallback.

That is enough to keep DelayBasin from oscillating between premature commitment and endless experiment bureaucracy.

## Transformer-facing implication

If this frame survives pressure, one transformer-facing implication is that the archive method may not only be discovering compact public state and compact public probes.
It may also be discovering compact public **decision boundaries for legitimate continuation**.

That is interesting because many ordinary “memory” framings stop at storage or retrieval, and many active-probe framings stop at better information acquisition.
DelayBasin instead would be preserving a small public rule for **when inquiry has done enough work to permit a new continuation act**.

The stronger reading — that this is approximating a public sequential test or stopping boundary over continuation space — remains quarantined.
