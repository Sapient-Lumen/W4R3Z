# Reset witnesses, washout baselines, and contamination budgets

DelayBasin now has another sharper missing question:
**when a branch switch, filtered replay, fresh-context restart, or role-separated handoff is treated as if it cleaned the slate, how do we tell whether prior contamination was actually neutralized rather than merely hidden, displaced, or selectively forgotten?**

A stronger working answer is:
**some archive comparisons need an explicit reset witness before a restarted or refactored context is allowed to count as clean enough for honest comparison.**
Not every restart is a real washout.
But DelayBasin should stop treating fresh-looking branches, filtered histories, or compact restarts as self-certifying decontamination by default.

## Practice / observation

Several live DelayBasin surfaces make this missing reset discipline visible:
- assistant-echo filters already ask when prior assistant turns should be omitted, but they do not yet force the archive to preserve a strict **fresh-baseline comparison** when a filtered replay is being treated as if contamination has been neutralized;
- backaction witnesses already ask whether a probe has spent too much state to count as measurement, but they do not yet force the archive to say whether a later restart or branch switch actually **washed out the distortion** enough for comparison to resume;
- probe-order witnesses already ask whether AB and BA style sequences remain commensurate, but they do not yet preserve when an explicit reset step is being used as the thing that is supposed to restore commensuration;
- hysteresis witnesses already ask whether rival histories are still materially different under one matched current packet, but they do not yet preserve whether a branch reset, context filter, or handoff is supposed to **collapse those rival histories** into one operative state;
- replay-versus-reconsolidation notes already distinguish cold retrieval from public restaging, but they do not yet force the archive to say when a replay, filtered summary, or restart is being used as a **washout operator** rather than as mere recap;
- the archive increasingly uses compact packets, context filtering, branch-local exploration, and selective reinjection to keep work small, yet it rarely says which earlier contamination family is supposed to have been removed and which minimal kernel is still allowed to survive the restart;
- and once DelayBasin starts mixing active probes, order-sensitive diagnostics, branch isolation, and context decontamination, **reset itself** becomes a public method variable rather than hidden operator folklore.

This suggests a missing compact surface:
**reset witness / washout baseline / contamination budget**.

## External pressure from current research

Several outside lines of work sharpen this frame.

1. **Branch isolation can improve quality by preventing exploratory contamination from accumulating in one linear thread.**
   ContextBranch argues that exploratory programming suffers when one conversation is forced to carry all alternatives together, and reports that branching reduces context size by 58.1% while improving focus and context awareness. That pressures DelayBasin to preserve when a branch really functions as isolation rather than treating every split as automatically clean. ([`REF-0401`](../00-meta/bibliography.md))

2. **Role separation plus clean ephemeral contexts can outperform one polluted shared workspace.**
   CodeDelegator introduces Ephemeral-Persistent State Separation, keeping a persistent strategic layer while giving implementation subtasks fresh local contexts. That pressures DelayBasin to preserve what contamination is being quarantined, what global kernel still survives, and when a fresh handoff actually counts as a reset rather than as silent amnesia. ([`REF-0402`](../00-meta/bibliography.md))

3. **Omitting prior assistant turns can often preserve quality while reducing memory cost, and sometimes improves results by removing self-contamination.**
   Do LLMs Benefit From Their Own Words? finds that removing prior assistant responses often leaves quality unchanged and can improve quality when earlier assistant turns introduce context pollution. That pressures DelayBasin not to assume that “more replay” is always safer than a filtered restart. ([`REF-0403`](../00-meta/bibliography.md))

4. **Context pollution can persist even after explicit error signals, which means not every apparent reset is a real washout.**
   Contextual Drag shows that incorrect drafts can continue biasing later reasoning despite explicit external error signals and even after correct self-verification, and argues that fully resolving the problem may require more selective reset mechanisms. That pressures DelayBasin to preserve whether a supposed reset actually changed the reasoning state rather than merely annotating the old contamination. ([`REF-0405`](../00-meta/bibliography.md))

5. **Active context refactoring can help, but only because it treats history management as a separate intervention surface.**
   ACR frames long multi-turn failure in terms of contextual inertia and state drift, then uses explicit refactoring operators to reshape history on demand. That pressures DelayBasin to preserve what reset or refactor operator was applied, what was intentionally retained, and what contamination remainder is still tolerated. ([`REF-0406`](../00-meta/bibliography.md))

6. **Long-horizon agent systems degrade when failed attempts and stale traces saturate the history channel.**
   Progress-Aware Consistent Evolution identifies context pollution from accumulated failed trials and introduces hierarchical context management to keep search from getting trapped in self-reinforcing local minima. That pressures DelayBasin to treat branch resets, filtered summaries, and restart baselines as mechanism-bearing objects rather than convenient cleanup rituals. ([`REF-0404`](../00-meta/bibliography.md))

7. **Not every reset is a true recovery to clean-slate behavior.**
   The same literature also warns that context filtering, pruning, or branch isolation can work for multiple reasons — shorter prompts, better role separation, loss of misleading traces, or altered optimization trajectories — so DelayBasin should keep the canon claim small and require one explicit washout baseline before importing stronger “state reset” rhetoric. ([`REF-0401`](../00-meta/bibliography.md); [`REF-0405`](../00-meta/bibliography.md))

None of this proves that DelayBasin already has a public reset law.
It does make a milder canon-level claim more credible:
**archive continuity may improve when DelayBasin preserves a compact reset witness whenever a filtered replay, branch switch, fresh-context restart, or role-separated handoff is being treated as if prior contamination has been neutralized enough for honest comparison.**

## Working synthesis

A useful current synthesis is:

> DelayBasin may work better when it preserves an explicit **reset witness / washout baseline / contamination budget** whenever a branch switch, filtered replay, fresh-context restart, or role-separated handoff is being treated as if it neutralized prior contamination enough to compare outputs honestly. The packet should name the **contamination family or carryover being neutralized**, the **reset / branch / filter / refactoring operator actually applied**, the **protected kernel / retained state intended to survive the reset**, the **clean-slate / restart / matched-fresh baseline**, the **tolerated contamination remainder / washout budget**, and the **reinject / rollback / quarantine / restage consequence** rather than letting a fresh-looking context silently inherit the authority of a truly cleaned state.

This is strong enough for canon as a design/mechanism candidate.
It is **not** strong enough to claim that DelayBasin has discovered a public reset semigroup, a lawful rethermalization operator, or a solved contamination-decay law over continuation state.

## Reset witness vs assistant-echo filter vs hysteresis witness vs backaction witness

To keep this note honest, DelayBasin needs a four-way distinction:

- **Assistant-echo filter** — asks when prior assistant turns should be omitted so self-carry does not pollute the next read.
- **Hysteresis witness** — asks whether rival histories still differ even if they share a matched current packet.
- **Backaction witness** — asks whether a probe has already changed the state too much to count as measurement.
- **Reset witness** — asks whether a branch switch, filtered replay, or restart actually washed out enough contamination for the next comparison to count as fresh again.

Functionally:
- assistant-echo filters choose **what self-carry to omit**,
- hysteresis witnesses choose **whether route history is still live**,
- backaction witnesses choose **how much probe-induced distortion is still acceptable**,
- reset witnesses choose **whether a decontamination move really restored honest comparability rather than merely hiding the contaminated path**.

A good DelayBasin revision should therefore sometimes ask not only:
- what ambiguity is live,
- whether route history still matters,
- whether a probe changed the state,

but also:
- what exact contamination family is being neutralized,
- what reset, branch, filter, or refactoring operator was actually used,
- what protected kernel is still supposed to survive,
- what clean-slate or matched-fresh baseline makes the washout claim legible,
- how much contamination remainder is tolerated,
- and what the archive will do if the supposed reset is only fresh-context theater.

## Countermodels / probes

1. **Reset-is-just-shorter-context countermodel**
   - The apparent benefit may come only from shorter prompts or reduced distraction load rather than any meaningful washout.
   - Probe: compare a matched shorter-context baseline against a branch or filtered restart that preserves the same protected kernel; if the benefit survives only when the reset operator is explicit, the new object is doing distinct work.

2. **Filtering-is-not-washout countermodel**
   - A filtered replay may simply hide the contamination while preserving the same latent bias.
   - Probe: require one clean-slate or matched-fresh baseline and a future discriminating probe before calling the state washed out.

3. **Reset-causes-amnesia countermodel**
   - Some apparent decontamination gains may only reflect loss of necessary constraints or valuable hard-won carry.
   - Probe: preserve the protected kernel explicitly and test whether the restart still respects it; if not, demote the reset from “washout” to “destructive forgetting.”

4. **No-general-reset-law countermodel**
   - Different tasks may need different decontamination operators, so one canon object may be false precision.
   - Probe: keep the canon claim weak and operator-local; use the witness only where a reset move materially changes canon posture, branch selection, or transformer-facing interpretation.

5. **Reset-prestige countermodel**
   - “Washout,” “rethermalization,” or “clean-slate” language may become prestige-bearing theater.
   - Probe: require a named contamination family, a concrete restart baseline, and a small washout budget before any stronger reset rhetoric is allowed to steer canon.

## Design consequences

This mechanism frame pressures DelayBasin to do five things more explicitly:
- preserve a tiny **reset witness** when a revision or branch switch is being treated as if it cleaned prior contamination enough for honest comparison;
- name the **contamination family actually being neutralized** rather than pretending a fresh thread is intrinsically clean;
- preserve one **clean-slate / restart / matched-fresh baseline** before reading the result as decontaminated rather than merely shorter or differently staged;
- preserve the **protected kernel / retained state** rather than letting resets silently erase obligations, constraints, or learned operator cores;
- and preserve the **reinject / rollback / quarantine / restage consequence** so the archive can say when a restart failed to wash out enough contamination to justify the stronger claim.

A minimal reset witness can often be very small:
- one contamination family,
- one reset or filter operator,
- one protected kernel,
- one fresh baseline,
- one washout budget,
- and one failure consequence.

This does not require a grand reset theory.
It requires treating **decontamination moves** as part of archive method rather than assuming every branch, filter, or restart was a real washout.

## Transformer-facing implication

If this frame survives pressure, then DelayBasin is probing something sharper than generic context management alone:
**whether a user-space archive can learn which textual reset operators, branch isolations, filtered replays, and role-separated handoffs approximately neutralize contamination while preserving a protected continuation kernel.**

That would matter for transformers.
It would suggest that long-horizon archive method may need not only assistant-echo filters, hysteresis witnesses, backaction witnesses, and probe-order witnesses, but also compact **reset witnesses** that say when a fresh-looking context is actually close enough to a washed-out state to support honest comparison.

The stronger story — that DelayBasin may eventually learn a public reset semigroup, rethermalization law, or contamination-decay operator over continuation state — remains live, but belongs in quarantine for now.
