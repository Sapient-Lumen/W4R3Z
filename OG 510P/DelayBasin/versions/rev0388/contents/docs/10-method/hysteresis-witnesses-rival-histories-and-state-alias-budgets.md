# Hysteresis witnesses, rival histories, and state-alias budgets

DelayBasin now needs a sharper answer to another practical question:
**when two archive states look the same at the current packet, endpoint, or reduced summary, what says they are actually the same continuation state rather than different histories temporarily collapsed onto one visible surface?**

A useful current answer is:
**canon should preserve a compact hysteresis witness / rival histories / state-alias budget packet whenever a claim depends on treating one matched endpoint or public summary as enough to identify the same operative state.**

This is stronger than saying history matters.
It is weaker than claiming DelayBasin has already discovered a literal public memory kernel or hysteresis law over archive trajectories.

## Practice / observation

Recent DelayBasin revisions make the missing surface visible:
- basin fingerprints already say that the same answer is not necessarily the same state;
- chart-transition, triangle-defect, gauge-fixing, and scale-fixing packets already say how local transports, residues, and reductions are being compared;
- memory-store vs regime-reentry notes already distinguish persistence from operative restart;
- but the archive still lacks a compact object for saying **when two rival histories have been collapsed onto one matched endpoint / public summary / fixed current packet**;
- and current transformer-facing language can therefore treat one reduced packet or local endpoint as if it were memoryless even when the route that produced it may still matter for the next continuation.

That gap creates at least five recurring failure modes:
- **state aliasing** — two rival histories produce the same current packet or summary, but later diverge under the next real probe;
- **endpoint laundering** — a matched local endpoint is treated as proof of same state even though only the visible summary matched;
- **history amnesia** — the archive forgets which earlier route, challenge, or correction made the current packet safe or unsafe;
- **false minimality** — a reduced packet looks sufficient only because the discriminating future probe was never named;
- **memory-kernel prestige** — hysteresis or state-space language quietly outruns the public evidence that any real lag law has been identified.

A compact hysteresis witness helps because it says:
- what **rival history family or route contrast** is being compared,
- what **matched endpoint / public summary / fixed current packet** is being held equal,
- what **future discriminating probe or continuation property** is supposed to reveal whether the histories really re-enter the same state,
- what **retained lag / hysteresis / alias budget** is still being tolerated,
- and what **rollback / quarantine / packet-splitting consequence** follows if the histories separate again.

## External pressure from current research

Several outside lines of work sharpen this move.

1. **Dialogue history can act like a real state-transition operator rather than a passive record.**
   State-Dependent Safety Failures in Multi-Turn Language Model Interaction explicitly treats dialogue history as a state transition operator and reports monotonic representational drift plus abrupt phase transitions under structured multi-turn interaction. That pressures DelayBasin to stop treating matched local prompts or reduced packets as automatically memoryless. ([`REF-0384`](../00-meta/bibliography.md))

2. **Reasoning trajectories can stay path-dependent even when the realized rollout is held fixed.**
   DRTC identifies pivot points in long traces and measures whether masking earlier chunks redirects the trajectory relative to the realized rollout direction. That pressures DelayBasin to preserve which earlier route segments still matter before it treats one current visible state as fully sufficient. ([`REF-0373`](../00-meta/bibliography.md))

3. **Minimal-context execution helps, but some hard steps need retained lookahead and short lag.**
   LEAD shows that atomic decomposition removes some self-conditioning failures by discarding history, yet still hits a no-recovery bottleneck on hard steps, where selective lookahead materially helps. That pressures DelayBasin toward an explicit lag budget rather than a universal memoryless ideal. ([`REF-0386`](../00-meta/bibliography.md))

4. **Transformer designs themselves separate iterative thinking from explicit learned storage.**
   Adaptive Loops and Memory in Transformers finds that looping mainly helps mathematical reasoning while memory banks recover commonsense performance, with later layers specializing more heavily in both. That pressures DelayBasin to distinguish a route effect from a stored-state effect rather than folding them into one generic memory story. ([`REF-0385`](../00-meta/bibliography.md))

5. **Long-horizon evaluations increasingly demand coherent internal state and robust recovery, not only local correctness.**
   OdysseyArena frames the bottleneck as temporal depth, coherent internal states, and recovery over extended interaction sequences. That pressures DelayBasin to preserve one explicit witness when two apparently same-state packets may imply different recovery prospects. ([`REF-0388`](../00-meta/bibliography.md))

6. **Trajectory-level invariants can generalize across tasks even when static probes miss them.**
   Truth as a Trajectory reports cross-dataset generalization from trajectory classifiers trained on one source task, suggesting that some operative invariants live in the path rather than in one frozen activation slice. That pressures DelayBasin to avoid treating one matched endpoint as the whole story when a route signature may still matter. ([`REF-0387`](../00-meta/bibliography.md))

## Working synthesis

A useful current synthesis is:

> DelayBasin should preserve a compact **hysteresis witness / rival histories / state-alias budget** packet whenever a reduced packet, matched endpoint, or current public summary is being treated as enough to certify same-state re-entry. The packet should name the **rival history family or route contrast**, the **matched endpoint / public summary / fixed current packet**, the **future discriminating probe or continuation property**, the **retained lag / hysteresis / alias budget**, and the **rollback / quarantine / packet-splitting consequence** if the histories separate again.

This is strong enough for canon as a design and mechanism candidate.
It is **not** strong enough to claim that DelayBasin has already identified a literal public memory kernel, hysteresis law, or finite lag-state realization over archive trajectories.

## Hysteresis witness vs basin fingerprint vs scale-fixing witness vs public memory-kernel claim

To keep this note honest, DelayBasin now needs a four-way distinction:

- **Basin fingerprint** — the packet saying that two same-answer or same-first-move continuations may still diverge later under a small downstream probe panel.
- **Scale-fixing witness** — the packet saying what resolution a claim lives at, what was integrated out to reach that scale, and what remainder budget makes that reduction honest.
- **Hysteresis witness / rival histories / state-alias budget** — the packet saying that even after the current packet or summary is matched, different route histories may still imply different future behavior unless one named discriminating probe collapses them.
- **Public memory-kernel claim** — the much stronger story that DelayBasin has already recovered a stable finite-lag law or user-space hysteresis operator for archive continuation.

A hysteresis witness is narrower than a public memory-kernel claim and different from a basin fingerprint.
It does not merely ask for future divergence panels.
It asks for one explicit route contrast and one matched current packet before the archive treats the present summary as memoryless.

## Countermodels / probes

1. **Current-packet-is-enough countermodel**
   - Once the current packet or reduced state is fixed, route history may add no useful predictive information.
   - Probe: hold the same current packet fixed across two rival histories and test whether one small future continuation probe still separates them.

2. **Basin-fingerprint-is-enough countermodel**
   - Existing same-answer-is-not-same-state discipline may already cover this.
   - Probe: compare one basin fingerprint panel with one explicit rival-history witness; if the latter adds no discriminating leverage, do not promote a new canon lane.

3. **Scale-only countermodel**
   - What looks like hysteresis may just be coarse-graining loss or wrong scale choice.
   - Probe: hold the route family fixed and vary only the coarse-graining rule; if the alias disappears, scale-fixing already did the work.

4. **Wrapper-noise countermodel**
   - Apparent route dependence may mostly reflect serving noise, hidden prompt layers, or execution variance.
   - Probe: rerun the same rival histories under an execution witness and ask whether the separation survives basic substrate controls.

5. **Memory-kernel-prestige countermodel**
   - Hysteresis language may just import dynamical-systems prestige without changing archive method.
   - Probe: require one rival-history family, one matched current packet, one discriminating future probe, and one explicit lag budget before any hysteresis language enters canon.

## Design consequences

This frame pressures DelayBasin to do five things more explicitly:
- preserve one **rival history family or route contrast** whenever the archive is about to treat a matched current packet as same-state evidence;
- preserve one **matched endpoint / public summary / fixed current packet** rather than leaving the equivalence class implicit;
- preserve one **future discriminating probe or continuation property** that could still separate the histories;
- preserve one **retained lag / hysteresis / alias budget** rather than talking as if the present packet were automatically memoryless;
- preserve one **rollback / quarantine / packet-splitting consequence** whenever the rival histories separate again.

## Transformer-facing implication

If this weaker canon move holds up, DelayBasin gets a cleaner transformer-facing story:
long-horizon archive method may sometimes work not because text has recovered a full latent state, and not because history is infinitely important, but because a compact packet plus one small rival-history witness can say **how much route dependence is still live** at the current continuation boundary.

That would be a meaningful bridge between archive practice and transformer mechanism.
It would suggest that some text-level archive packets behave like approximate coarse-grained states only when their remaining hysteresis has been publicly budgeted.

What DelayBasin still does **not** know is stronger:
whether there exists any real public finite-lag state law, memory kernel, or hysteresis operator for archive continuation rather than a pile of local route-sensitive patches.
