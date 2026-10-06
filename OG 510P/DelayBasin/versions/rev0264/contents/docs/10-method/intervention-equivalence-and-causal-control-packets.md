# Intervention-equivalence and causal-control packets

DelayBasin now has a sharper bounded-state question than “what future family is preserved under compression?”
The next question is:
**when do two archive surfaces remain observationally similar while still implying different next interventions, challenge probes, or admissible continuation decisions?**

A useful working answer is:
**two bounded-state candidates should only be merged when they are intervention-equivalent for the bounded family of probes, repairs, or continuation moves DelayBasin still intends to make.**
If the next cheap intervention or challenge probe branches differently, the distinction has not yet earned compression.

This is stronger than passive predictive sufficiency.
It is weaker than claiming that DelayBasin has already isolated a literal public causal model, do-calculus, or intervention algebra over continuation space.

## Practice / observation

Several existing DelayBasin surfaces already behave as though passive recap is not enough:
- control-authority packets matter because the archive cares which actuator surface is expected to move which target property, not only what future prose might say;
- identification packets matter because the archive often needs the next observation or probe that will split rival continuation hypotheses before canon moves;
- sentinel panels and witness sets matter because some distinctions stay dormant until the archive deliberately stresses a boundary;
- hold packets matter because the archive sometimes needs to preserve not only uncertainty, but what concrete probe or repair would unlock motion;
- and future-equivalence compression already assumes that a bounded family of interventions belongs inside the preserved future family, even if the archive has not yet separated passive from active equivalence clearly enough.

Taken together, these surfaces pressure DelayBasin toward a stricter bounded-state rule:
not merely “keep what predicts the next read,” and not even only “keep what preserves a future family,” but “keep distinctions that still change what the archive should try, test, or permit next.”

## Mechanism pressure from outside the archive

Several outside lines of work sharpen this move.

1. **Causal abstraction can be optimized for intervention, not just prediction.**
   Simões, Dastani, and van Ommen's causal information bottleneck explicitly compresses variables while maintaining causal control over a target and frames the result as usable for intervention reasoning. That is direct pressure against DelayBasin treating observational similarity as sufficient when intervention choice is the live question. ([`REF-0177`](../00-meta/bibliography.md))

2. **Causal-state work in partial observability already links compression to action-conditioned equivalence.**
   Zhang et al. treat causal states as the coarsest partition of action-observation histories in a POMDP and connect the construction to bisimulation. That matters here because DelayBasin is not trying to preserve pretty historical distinctions; it is trying to preserve distinctions that still alter future probe or action consequences. ([`REF-0176`](../00-meta/bibliography.md))

3. **Current state-representation work treats behavioral equivalence as a compactness criterion for control.**
   The recent survey of state representation learning emphasizes bisimulation as a way to aggregate states while preserving reward and transition structure, covers lax state-action equivalence, and notes action-bisimulation variants that replace reward similarity with control-relevant terms. That is strong pressure for DelayBasin to ask whether two packet states are equivalent for action, not only equivalent for description. ([`REF-0178`](../00-meta/bibliography.md))

4. **Bisimulation losses are now being used directly for robust control representations.**
   Shimizu and Tomizuka's BS-MPC paper uses bisimulation loss to optimize encoders that discard irrelevant details while improving stability, robustness to input noise, and efficiency in model-predictive control. That is outside evidence that compactness criteria become more useful when they preserve action-relevant structure rather than recap detail. ([`REF-0179`](../00-meta/bibliography.md))

5. **Useful compact hypotheses often earn their keep by generating counterexample search, not by recap alone.**
   Anthropic's property-based testing writeup describes an agent that infers general properties and then searches for counterexamples by generating tests. That is a useful analogue for DelayBasin: a bounded packet may deserve carry-forward status when it cheaply generates the next discriminating probe or falsification attempt, not merely when it restates what the archive already believes. ([`REF-0180`](../00-meta/bibliography.md))

## Working synthesis

A useful current synthesis is:

> DelayBasin should preserve **causal-control packets** whenever two bounded-state candidates are observationally close but not yet intervention-equivalent. A distinction deserves bounded-state residency when collapsing it would change the next cheap probe, repair attempt, challenge move, or admissible continuation decision the archive still cares about.

In practice, DelayBasin is not estimating a full causal graph over continuation space.
It is doing something smaller and public:
- name the relevant intervention family,
- name the target property or continuation decision the intervention is supposed to affect,
- and name the first branch divergence that would show two surfaces were not safely mergeable after all.

That is strong enough for canon as a compression and testing discipline.
It is **not** strong enough to claim that DelayBasin has already recovered a public intervention algebra or causal bottleneck over continuation space.

## Passive-future equivalence vs intervention-equivalence vs local probe

To keep this note honest, DelayBasin needs a three-way distinction:

- **Passive-future equivalence** — two surfaces appear equivalent for a bounded family of read-only predictions or recap questions.
- **Intervention-equivalence / causal-control packet** — two surfaces stay equivalent even when the archive considers the bounded probe, repair, or challenge interventions it may actually attempt next.
- **Local probe object** — a witness panel, sentinel, or one-off challenge packet that may separate one fragile branch without deserving durable bounded-state status by itself.

These are related but not identical.
A packet can look observationally redundant while still implying different intervention branches.
An intervention-equivalent packet is stronger than a merely predictive one because it survives the next active move class the archive still intends to use.
And a local probe may matter for one branch without defining the archive's broader control-relevant quotient.

## Countermodels / probes

1. **Passive-alias countermodel**
   - Two surfaces may appear safely merged only because the archive checked read-only questions and not the next real intervention family.
   - Probe: compare the next cheap challenge, repair, or actuation step; if the branch choice changes, the merge was premature.

2. **Overactive-probe countermodel**
   - Intervention language may excuse keeping too many distinctions alive because every surface can be tied to some hypothetical action.
   - Probe: require a bounded intervention family tied to an actual near-term continuation decision, not an unconstrained universe of imaginable actions.

3. **Property-theater countermodel**
   - Generalized property language may sound rigorous while generating no real counterexample search.
   - Probe: ask whether the packet produces a concrete next test, challenge probe, or repair attempt that could fail.

4. **Family-specific action aliasing countermodel**
   - Two surfaces may be intervention-distinct for one model family or prompt-pair regime but equivalent for another.
   - Probe: compare colder reopens, paraphrased reopens, or family-shifted reopens and see whether the same intervention split still changes the same decision.

5. **Evidence-does-all-the-work countermodel**
   - Ordinary evidence and check packets may explain most of the gain, with explicit intervention-equivalence language adding little.
   - Probe: hold evidence/check discipline fixed while varying whether bounded-state compression explicitly names intervention family, target property, and branch divergence.

## Design consequences

This frame pressures DelayBasin to do five things more explicitly:
- when compressing bounded state, ask **what intervention family is preserved, not only what read-only future family?**
- ask **what target property, repair path, or continuation decision remains invariant under the merge?**
- name **the first branch divergence** that would prove two surfaces were not intervention-equivalent;
- prefer bounded packets that cheaply generate next probes, challenge tests, or repair attempts over packets that only improve retrospective narration;
- and keep stronger causal-bottleneck / intervention-algebra language quarantined until explicit branch tests show real leverage beyond future-equivalence rhetoric.

## Transformer-facing implication

If this frame survives pressure, then DelayBasin is probing something sharper than compact predictive state and sharper than passive future-equivalence.
It is probing whether a public archive can learn a **control-relevant quotient over continuation space**: a user-space partition where different past packet states are treated as equivalent only when they induce the same bounded interventions, challenge branches, and admissible continuation decisions.

That is transformer-facing in a distinct way.
It suggests that archive continuity may improve not only by caching future-useful distinctions, but by discovering which public distinctions remain causally live for the next action-conditioned branch under bounded context.

The stronger claim that DelayBasin is discovering a literal public causal bottleneck, intervention algebra, or do-equivalence quotient over continuation space remains quarantined until controlled branch tests show that explicit intervention-equivalence discipline outperforms passive predictive compression without re-inflating the archive into action fantasy.
