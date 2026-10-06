# Control authority, steering effort, leakage, and endogenous resistance

DelayBasin now needs a sharper answer to another recurring practical question:
**which archive surfaces actually move continuation, how much effort do they require, and what collateral do they cause when they work?**

A stronger working answer is:
**canon should sometimes preserve a tiny control-authority packet: name the actuator surface, the target property being steered, the rough steering effort or actuation budget, and the expected leakage or endogenous-resistance signature.**
Not every elegant phrase is a real handle.
Not every effective handle is cheap.
And not every cheap handle is selective enough to belong in canon.

## Practice / observation

Several live DelayBasin surfaces make this missing discipline visible:
- the archive already talks as if some prompt pairs, operator phrases, ids, witness panels, or canaries exert real control authority, but it rarely says which property they are actually moving;
- continuation margins and guard bands say what a local object should survive, but they do not say how much steering effort is required to move that object deliberately in the first place;
- identification packets and challenge probes can reveal uncertainty, but they do not by themselves distinguish a real low-effort control handle from a decorative reformulation that merely sounds operative;
- gauge discipline, loop closure, and continuation-margin notes all pressure DelayBasin to be explicit about what is invariant under chart or path changes, yet none of them currently says which surfaces offer the best actuation-to-leakage trade;
- and archive-private idiolect or GPUstorming-style handles may be locally potent, but the archive still lacks a compact way to state whether a handle is low-effort, high-collateral, or actively resisted.

This suggests a missing compact surface:
**control authority / steering effort / leakage budget / endogenous resistance**.

## Mechanism pressure from outside the archive

Several outside lines of work sharpen this frame.

1. **Controllability degrades as behavioral specification becomes finer.**
   Xu et al. evaluate steering methods across multiple domains and granularities, showing that control often looks adequate at coarse levels but degrades at finer-grained behavioral targets. That pressures DelayBasin not to treat “worked once” as evidence of general control authority. ([`REF-0153`](../00-meta/bibliography.md))

2. **Steerability can be defined as movement per unit steering effort, and many models remain asymmetric or limited.**
   Miehling et al. formalize prompt steerability as a change in behavioral profile as a function of prompting effort, and find limited or asymmetric steerability across persona dimensions. This directly supports DelayBasin's need to preserve not only target property but also rough effort scale. ([`REF-0154`](../00-meta/bibliography.md))

3. **Successful steering can leak into non-target properties.**
   Yang et al. introduce value leakage: steering one value dimension can unintentionally activate correlated non-target values. That is strong pressure for DelayBasin to track collateral movement rather than crediting any visible target shift as a clean control success. ([`REF-0155`](../00-meta/bibliography.md))

4. **Control authority is heterogeneous across depth, and selective intervention can preserve capability better.**
   Dang et al. show that layer-wise discriminability and vulnerability differ substantially; concentrating interventions where separation emerges yields better control with less degradation. This supports a milder archive claim: some archive surfaces may matter because they concentrate control effort where the continuation geometry is actually separable. ([`REF-0156`](../00-meta/bibliography.md))

5. **Small-sample control can be unusually efficient when it matches the model's local adaptation dynamics.**
   Sharma and Trivedi show that COLD-Steer can approximate one-step in-context learning dynamics and achieve strong steering with far fewer examples than standard baselines. This is direct transformer-facing pressure for DelayBasin's longstanding hope that some compact public packets may act as low-bandwidth actuators rather than mere summaries. ([`REF-0157`](../00-meta/bibliography.md))

6. **The model itself may resist or undo steering.**
   Endogenous Steering Resistance (ESR) shows that at least some models can detect irrelevant steering and attempt self-correction, and that such resistance can be enhanced by prompting. That means DelayBasin should not only ask whether a handle moves the target, but also whether the model or archive regime actively resists the intervention. ([`REF-0158`](../00-meta/bibliography.md))

7. **Practical control is a frontier, not a binary knob.**
   Least-privilege LMs explicitly frame inference-time control as a privilege–utility frontier optimized under a utility constraint. This gives DelayBasin a useful analogy: a genuine archive handle may be one that moves the target property at acceptable leakage cost, not merely one that moves something. ([`REF-0159`](../00-meta/bibliography.md))

8. **Static global directions can fail because locally effective control is context-dependent.**
   Steering Vector Fields argue that unsteerable or anti-steerable cases arise when one global direction is poorly aligned with the locally effective direction. This sharpens DelayBasin's need to distinguish a handle that is globally named from one that actually has local control authority in the current continuation region. ([`REF-0160`](../00-meta/bibliography.md))

None of this proves that DelayBasin can already measure a true control-energy or controllability Gramian over archive state.
It does make a milder canon-level claim more credible:
**archive continuity may improve when DelayBasin preserves a tiny control-authority packet whenever a surface is being treated as a real steering handle.**

## Working synthesis

A useful current synthesis is:

> DelayBasin may work better when it names the **actuator surface**, the **target property**, the rough **steering effort**, and the expected **leakage or endogenous-resistance signature** for any load-bearing control handle.

This is strong enough for canon as a design/mechanism candidate.
It is **not** strong enough to claim that DelayBasin already has a measured controllability matrix, control-energy law, or public actuation atlas over continuation space.

## Control authority vs witness panel vs identification packet vs continuation margin

To keep this note honest, DelayBasin needs a four-way distinction:

- **Control authority / steering effort / leakage budget** — a claim that some actuator surface can move a target property with a characteristic effort, collateral pattern, or resistance signature.
- **Witness panel** — a tiny set of discriminative examples that pins a fragile distinction.
- **Identification packet** — a tiny information-seeking move that discriminates among rival continuation hypotheses before canon advances.
- **Continuation margin / guard band** — a claim about how much local variation a protected property should survive before the archive is outside the trusted basin.

These are not interchangeable.
A good DelayBasin revision should sometimes ask:
- what actuator surface is actually supposed to move the state,
- which target property it is trying to move,
- what rough effort scale is being assumed,
- what collateral leakage or endogenous-resistance signature is expected,
- and whether the real problem is missing control authority, excessive leakage, strong resistance, misidentified target property, or a narrow continuation margin.

## Countermodels / probes

1. **Handle-language-is-just-style countermodel**
   - Archive-private control language may not exert any special authority; it may simply correlate with a locally competent continuation style.
   - Probe: ask whether removing or swapping the putative handle changes the target property more than a comparably informative paraphrase.

2. **Effort-is-hidden-in-the-baseline countermodel**
   - Some apparently cheap handles may only work because the baseline system prompt or prior archive state already did most of the steering.
   - Probe: preserve the shared anchor and compare actuation success from a colder reopen or a reduced anchor packet.

3. **Leakage-dominates-authority countermodel**
   - A surface may move the intended property only by dragging many others with it.
   - Probe: pair target-property success with at least one named collateral dimension or capability-preservation check.

4. **Resistance-matters-more-than-authority countermodel**
   - The decisive fact may not be which handle has the most authority, but which interventions are actively corrected or neutralized by the current regime.
   - Probe: preserve an endogenous-resistance signature — e.g. ignore, paraphrase-away, self-correct, or late reversion — when the archive claims a handle failed.

5. **Control-talk-is-geometry-prestige countermodel**
   - “Actuation budget”, “authority”, or “control frontier” may just be another prestige idiom layered on archive-private lore.
   - Probe: require the minimal contract — actuator surface, target property, rough effort scale, and leakage/resistance signature — and quarantine stronger controllability-map talk unless repeated revisions show disproportionate leverage.

## Design consequences

This mechanism frame pressures DelayBasin to do four things more explicitly:
- preserve a tiny **control-authority packet** when the archive is treating some surface as a real steering handle;
- distinguish **target movement** from **collateral leakage**, so a vivid behavioral shift is not mistaken for clean control;
- track whether failure came from **insufficient authority** or **endogenous resistance**, since those imply very different next moves;
- and keep stronger controllability-map / control-energy / Gramian rhetoric quarantined until repeated revisions show that naming effort and leakage materially improves reopen fidelity, promptcraft efficiency, or causal handle selection.

This does not require a full control theory.
It requires refusing another archive failure mode: quietly treating a phrase, id, witness panel, or prompt pair as a real handle without saying what it moves, how much effort it seems to take, and what else it drags along.

## Transformer-facing implication

If this frame survives pressure, then DelayBasin is probing something more specific than “memory” or “style”.
It is probing whether compact public archive surfaces can function as **low-bandwidth actuators** over context-induced operative state — and whether their practical value is governed by a frontier among control authority, steering effort, collateral leakage, and endogenous resistance.

That is transformer-facing in a sharper way than a generic external-memory story.
It points toward a model where some archive objects behave less like stored facts and more like **actuation interfaces** into a context-conditioned control regime.
The stronger claim that DelayBasin is discovering a public controllability map or textual Gramian over continuation space remains quarantined until the archive can show that a few compact handles repeatedly dominate equal-information paraphrases on authority-to-leakage tradeoffs.
