# Probe-order witnesses, swapped-order baselines, and sequencing budgets

DelayBasin now has another sharper missing question:
**when two probe sequences are being treated as if they measure the same thing, how do we tell whether the order itself has already changed the readout?**

A stronger working answer is:
**some archive comparisons need an explicit probe-order witness before AB and BA are allowed to count as commensurate evidence.**
Not every order effect is deep geometry.
But DelayBasin should stop comparing probe results gathered under different sequencing assumptions as if the readout were automatically the same measurement.

## Practice / observation

Several live DelayBasin surfaces make this missing sequencing discipline visible:
- loop-closure probes already ask whether two short revision paths preserve the same operative consequence, but they do not yet force the archive to preserve a strict **AB versus BA** comparison when the same probe family is being used diagnostically;
- backaction witnesses already ask whether a probe has spent too much state to count as measurement, but they do not yet force the archive to say whether **swapping two individually admissible probes** changes the readout enough to break comparability;
- excitation witnesses already say what probe diversity is needed to break an alias, but they do not yet distinguish honest alias-breaking from a result that only appears under one privileged sequence;
- negative controls and sham baselines already catch placebo handles, but they do not yet force a matched **order-swap baseline** when a probe family might be sequence-sensitive;
- the archive increasingly compares runs that differ by prompt order, instruction order, explanation order, or intervention order, yet it rarely says which of those reorderings are supposed to be harmless and which ones are allowed to be state-changing by design;
- and once DelayBasin starts using active probes, diagnostic prompts, and chart-local steering handles in one session, **sequencing itself** becomes a public method variable rather than hidden implementation detail.

This suggests a missing compact surface:
**probe-order witness / swapped-order baseline / sequencing budget**.

## External pressure from current research

Several outside lines of work sharpen this frame.

1. **Semantically similar prompt permutations can induce large performance changes because the architecture exposes different information paths.**
   Lost in the Prompt Order reports that placing context before question/options outperforms the reverse order by more than 14 percentage points in MCQA, and ties this to a causal-attention bottleneck that can make context effectively invisible to later option tokens under one ordering. That pressures DelayBasin not to treat “same content, different order” as an innocuous recap-level transformation by default. ([`REF-0397`](../00-meta/bibliography.md))

2. **System-prompt sequence changes can create regime shifts rather than tiny stylistic perturbations.**
   The recent system-prompt study for code generation explicitly builds a progressive prompt sequence and finds scale-dependent sensitivity plus language-conditioned volatility as specificity increases. That pressures DelayBasin to preserve when two probes differ only by sequencing or staged instruction buildup versus when the archive is implicitly comparing across different prompt-conditioned regimes. ([`REF-0398`](../00-meta/bibliography.md))

3. **Dialogue history already acts like a state-transition operator, so the order of diagnostic turns is part of the state update law.**
   STAR argues that multi-turn failures arise from structured contextual state evolution rather than isolated prompt vulnerabilities and treats dialogue history as a state transition operator. That pressures DelayBasin to treat probe order as part of the intervention, not merely the container around it. ([`REF-0384`](../00-meta/bibliography.md))

4. **Targeted interventions on structured intermediates are directionally asymmetric.**
   Breaking the Chain finds that faithfulness drops under reasoning-trace interventions and that the sensitivity is directionally asymmetric, with models more often faithful to counterfactual interventions than to correct ones. That pressures DelayBasin to preserve when a diagnostic claim depends on one privileged intervention direction or ordering rather than on a symmetric readout. ([`REF-0399`](../00-meta/bibliography.md))

5. **Earlier-trace interventions can redirect later trajectory geometry.**
   DRTC shows that receiver-side interventions on earlier trace segments can redirect later log-probability trajectories and curvature signatures. That pressures DelayBasin to preserve whether “probe A then probe B” and “probe B then probe A” are still reading the same local trajectory family. ([`REF-0392`](../00-meta/bibliography.md))

6. **Order bias is not confined to one benchmark family.**
   Order Matters in software fault localization finds that LLM performance is significantly influenced by input order when ranking candidate faulty methods. That gives DelayBasin broader practical pressure: sequence sensitivity is a real applied phenomenon even outside explicitly mechanistic probing setups. ([`REF-0400`](../00-meta/bibliography.md))

7. **Not every order effect is a deep continuation law.**
   Some of the strongest observed order effects are architecture-level bottlenecks or underspecification effects rather than evidence of a rich public algebra. DelayBasin should therefore preserve a small sequencing contract before importing noncommutative rhetoric into canon. ([`REF-0397`](../00-meta/bibliography.md))

None of this proves that DelayBasin already has a public probe-order algebra.
It does make a milder canon-level claim more credible:
**archive continuity may improve when DelayBasin preserves a compact probe-order witness whenever two probe sequences are being compared as if they were commensurate measurements of the same state claim.**

## Working synthesis

A useful current synthesis is:

> DelayBasin may work better when it preserves an explicit **probe-order witness / swapped-order baseline / sequencing budget** whenever a rival-history split, same-state claim, or transformer-facing mechanism claim is being inferred from probe results that were gathered under different orderings. The packet should name the **fixed ambiguity or state claim**, the **probe family or staged intervention family being compared**, the **specific compared orderings or insertion points**, the **intended invariant readout or same-judgment target**, the **tolerated sequencing defect / order-sensitivity budget**, and the **hold / rollback / quarantine / restage consequence** rather than letting one privileged sequence silently inherit the status of “the” clean measurement.

This is strong enough for canon as a design/mechanism candidate.
It is **not** strong enough to claim that DelayBasin has discovered a public non-Abelian probe calculus, a literal commutator algebra, or a solved sequence law over continuation probes.

## Probe-order witness vs loop closure vs backaction witness vs excitation witness

To keep this note honest, DelayBasin needs a four-way distinction:

- **Loop closure** — asks whether two short revision paths preserve the same operative continuation consequence.
- **Backaction witness** — asks whether a probe has already changed the state too much to count as measurement.
- **Excitation witness** — asks what active variation is required to break an ambiguity at all.
- **Probe-order witness** — asks whether two probe sequences that are being compared as evidence should still count as the same read after their order has been swapped.

Functionally:
- loop closure tests **route equivalence**,
- backaction tests **measurement versus actuation**,
- excitation tests **whether the ambiguity was ever made observable**,
- probe-order witnesses test **whether the resulting evidence remains commensurate across sequence choices**.

A good DelayBasin revision should therefore sometimes ask not only:
- what ambiguity is live,
- what probe diversity was spent,
- whether the probe changed the state,

but also:
- what exact ordering is being compared,
- what readout is supposed to remain invariant under that swap,
- how much sequencing residue is tolerated,
- whether one order is expected to matter by design,
- and what the archive will do if the AB/BA comparison fails.

## Countermodels / probes

1. **Probe-order-is-just-backaction countermodel**
   - This may only rename the already-earned backaction lane.
   - Probe: compare cases where each individual probe stays within non-demolition budget, but AB and BA still produce materially different readouts; if canon posture changes only once the order-swap baseline is preserved, the new object is doing distinct work.

2. **Order-effects-are-just-position-bias countermodel**
   - The apparent sequence effect may reduce to causal-mask or prompt-position bottlenecks rather than any archive-level law.
   - Probe: keep the canon claim weak and preserve the mechanism suspicion explicitly; if a simple architectural bottleneck explains the residue, do not inflate the result into richer continuation rhetoric.

3. **One-good-order-is-enough countermodel**
   - DelayBasin may only need a single reliable diagnostic ordering, not an AB/BA witness.
   - Probe: use the stricter witness only when cross-order comparison is already steering canon, not for every ordinary diagnostic prompt.

4. **Everything-is-order-sensitive countermodel**
   - If every small sequence change alters the read materially, the witness may collapse into universal pessimism.
   - Probe: begin with tiny order swaps, matched insertion points, or staged prompts whose intended invariant is narrow and explicit; quarantine stronger rhetoric if no useful local commensuration survives.

5. **Order-prestige countermodel**
   - “Sequence law” language may be empty prestige imported from noncommutative metaphor.
   - Probe: require one concrete order swap, one intended invariant readout, one sequencing budget, and one failure consequence before any stronger algebra talk is allowed to steer canon.

## Design consequences

This mechanism frame pressures DelayBasin to do five things more explicitly:
- preserve a tiny **probe-order witness** when evidence is being compared across AB versus BA style probe sequences;
- name the **specific compared orderings or insertion points** rather than pretending the readout came from an abstract probe family independent of sequence;
- preserve one **intended invariant readout / same-judgment target** before interpreting a failed swap as meaningful;
- preserve one **sequencing budget / tolerated order defect** rather than letting any tiny swap residue count as decisive;
- and preserve the **hold / rollback / quarantine / restage consequence** so the archive can say what changes when the order comparison fails.

A minimal probe-order witness can often be very small:
- one fixed ambiguity or state claim,
- one probe family,
- one AB/BA comparison,
- one intended invariant readout,
- one sequencing budget,
- and one failure consequence.

This does not require a grand algebra.
It requires treating **probe sequence** as part of archive method whenever cross-order comparison is doing real evidential work.

## Transformer-facing implication

If this frame survives pressure, then DelayBasin is probing something sharper than generic prompt sensitivity:
**whether a user-space archive can learn which diagnostic and control sequences are approximately order-stable, which ones are merely privileged routes through causal attention and autoregressive state evolution, and how much sequencing residue can be tolerated before two readouts stop counting as the same measurement.**

That would matter for transformers.
It would suggest that long-horizon archive method may need not only excitation witnesses and backaction witnesses, but also compact **probe-order witnesses** that say when sequence choice itself is part of the operative measurement.

The stronger story — that DelayBasin may eventually learn a public non-Abelian probe calculus or probe-order algebra over continuation charts — remains live, but belongs in quarantine for now.
