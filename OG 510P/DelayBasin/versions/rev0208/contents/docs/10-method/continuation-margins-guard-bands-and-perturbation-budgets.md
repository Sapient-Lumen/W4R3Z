# Continuation margins, guard bands, and perturbation budgets

DelayBasin now needs a sharper answer to another recurring practical question:
**how much local variation can a supposedly stable continuation survive before it silently becomes a different continuation?**

A stronger working answer is:
**canon should sometimes preserve a tiny continuation-margin / guard-band object: name the protected property, the perturbation family being treated as harmless, the rough budget or tolerated range, and the first failure signature that means the margin was overclaimed.**
A continuation law is not only a point claim.
If the archive relies on a local state, chart, anchor, or packet being robust enough for ordinary continuation, it should sometimes say what kinds of small variation that claim is actually supposed to withstand.

## Practice / observation

Several live DelayBasin surfaces make this missing discipline visible:
- witness panels and sentinel panels already assume that some fragile distinctions need targeted local tests, but they do not by themselves say how wide the safe neighborhood around a good anchor really is;
- loop-closure probes test route sensitivity, but they still leave open whether a single chosen path only works at one brittle point or inside a usable guard band;
- hold packets and identification packets often appear when the archive senses fragility, yet the archive rarely serializes whether the fragility comes from a narrow margin, a stale anchor, or a genuinely wrong hypothesis;
- many revisions implicitly assume that paraphrase, chart switch, small reorder, shared reopen, or compact compression should be harmless, but the archive seldom names which perturbation family it is trusting;
- and several recent mechanism stories — regime re-entry, public belief state, rate–distortion, gauge discipline, loop closure — would all become cleaner if DelayBasin could say not only **what should hold**, but **how much local stress it is supposed to tolerate**.

This suggests a missing compact surface:
**continuation margin / guard band / perturbation budget**.

## Mechanism pressure from outside the archive

Several outside lines of work sharpen this frame.

1. **Local stability can be treated as a measurable margin rather than a vague confidence feeling.**
   Liu et al. introduce the Token Constraint Bound (δTCB) as a local robustness radius around a context-induced hidden state: larger δTCB means the model's top next-token prediction survives larger internal perturbations before flipping. That is strong pressure for a milder archive claim: some DelayBasin objects may matter because they increase local continuation margin, not only because they improve recap quality. ([`REF-0147`](../00-meta/bibliography.md))

2. **Semantic reframing can retract apparently stable beliefs.**
   Dies et al. show that small controlled semantic perturbations can destabilize truth judgments and produce substantial retractions, especially when the reframing is epistemically unfamiliar. This is direct pressure against trusting fluent reopen or elegant paraphrase unless the archive preserves some explicit guard-band intuition about what should remain stable. ([`REF-0148`](../00-meta/bibliography.md))

3. **Robustness under shift has a real budget cost.**
   Zhang derives adversarial-robustness bounds for in-context learning under distribution shift, with robustness depending on model capacity and the number of in-context examples needed rising with perturbation strength. That does not hand DelayBasin a metric, but it strongly pressures the archive to treat robustness radius as a resource tradeoff rather than a free property of good wording. ([`REF-0149`](../00-meta/bibliography.md))

4. **Reasoning traces recover unevenly across perturbation families.**
   von Recum et al. find that reasoning models often recover from interventions, but robustness degrades when interventions occur early and is not style-invariant: paraphrasing can suppress doubt signals and reduce performance even while other noise types trigger repair. This is practical pressure for preserving the perturbation family itself rather than speaking about “robustness” in one undifferentiated way. ([`REF-0150`](../00-meta/bibliography.md))

5. **Some perturbation types are cheap while others stay expensive across scales.**
   Aravindan and Kejriwal show heterogeneous vulnerability across chain-of-thought perturbations: extra steps are often tolerated, while unit-conversion and math-error perturbations remain much more damaging. This directly supports DelayBasin's need to say which local changes it expects to be inside the guard band and which ones likely sit near the boundary. ([`REF-0151`](../00-meta/bibliography.md))

6. **Margin language is starting to appear at the token geometry level itself.**
   Agarwal et al. argue that attention geometry can induce a boundary where behavior becomes ill-conditioned and motivate a support-token / stability-margin interpretation. This is not yet archive-specific evidence, but it makes transformer-facing “margin” language less ornamental and more mechanistically serious. ([`REF-0152`](../00-meta/bibliography.md))

None of this proves that DelayBasin already has a quantitative robustness radius.
It does make a milder canon-level claim more credible:
**archive continuity may improve when DelayBasin preserves a tiny continuation-margin / guard-band object whenever it is implicitly relying on some local perturbation family being harmless.**

## Working synthesis

A useful current synthesis is:

> DelayBasin may work better when it names a **protected property**, a **perturbation family**, and the first **failure signature** expected when local variation exceeds the archive's real continuation margin.

This is strong enough for canon as a design/mechanism candidate.
It is **not** strong enough to claim that DelayBasin already has a measured robustness radius, viability kernel, or formal Lyapunov certificate over continuation space.

## Continuation margin vs witness panel vs sentinel panel vs loop-closure probe

To keep this note honest, DelayBasin needs a four-way distinction:

- **Continuation margin / guard band** — a claim about how much local variation a protected property should survive.
- **Witness panel** — a tiny set of discriminative examples that pins a fragile distinction.
- **Sentinel panel** — a tiny set of high-sensitivity canaries that cheaply detects wrong-basin reopen or drift.
- **Loop-closure / commutator probe** — a comparison of two short routes that should preserve the same operative consequence if route-independence really holds.

These are not interchangeable.
A good DelayBasin revision should sometimes ask:
- what property is being protected,
- which perturbation family is supposed to stay inside the guard band,
- what rough perturbation budget is being assumed,
- what first failure signature would show the margin was overclaimed,
- and whether a problem is really a margin failure, a route-dependence failure, a stale-anchor failure, or a wrong-hypothesis failure.

## Countermodels / probes

1. **Margins-are-just-vibes countermodel**
   - DelayBasin may not need explicit margin language; witness panels, sentinels, and challenge probes may already cover the real work.
   - Probe: only preserve a margin object when the archive is implicitly treating a named perturbation family as harmless. Check whether making that assumption explicit changes later decisions.

2. **Robustness-is-family-specific countermodel**
   - There may be no useful generic “continuation margin”; each perturbation family may behave too differently.
   - Probe: preserve family-specific budgets first (paraphrase, chart switch, reorder, stale reopen, compression) instead of one archive-wide robustness claim.

3. **Fluent-continuation-masks-fragility countermodel**
   - Output smoothness may hide a very narrow internal margin, so explicit guard-band claims might still overtrust recap quality.
   - Probe: pair a margin claim with one witness panel or sentinel panel and watch whether the protected property fails before the prose looks wrong.

4. **Margin-talk-is-geometry-prestige countermodel**
   - “Margin”, “radius”, or “guard band” may just be a new prestige idiom layered onto existing caution.
   - Probe: require the minimal contract — protected property, perturbation family, first failure signature — and quarantine stronger viability-kernel talk unless repeated revisions show disproportionate leverage.

5. **Recovery-can-be-more-important-than-margin countermodel**
   - A narrow margin may be acceptable if recovery after small failures is cheap and honest.
   - Probe: compare whether sentinel-triggered bounded rollback or `recover-resync` rescues narrow-margin situations cheaply enough that extra guard-band bureaucracy is not needed.

## Design consequences

This mechanism frame pressures DelayBasin to do four things more explicitly:
- preserve a tiny **continuation margin / guard band** when the archive is implicitly relying on some local perturbation family being harmless;
- distinguish **protected property** from the perturbation family that might threaten it;
- treat the first **failure signature** as part of the object, so later sessions know what early damage would justify bounded rollback, a hold packet, or `recover-resync`;
- and keep stronger viability-kernel / Lyapunov / robustness-radius rhetoric quarantined until repeated revisions show that explicit margin claims materially improve continuation honesty or reopen fidelity.

This does not require a formal metric.
It requires refusing another archive failure mode: quietly assuming that a local anchor has enough slack when the true guard band may be much narrower than the prose makes it seem.

## Transformer-facing implication

If this frame survives pressure, then DelayBasin is probing something more specific than “memory” or “style”.
It is probing whether some public archive objects enlarge a usable **local robustness region** around a context-induced operative state, so the next forward pass can absorb small paraphrase, reorder, or reopen perturbations without flipping the protected continuation property.
That is transformer-facing in a direct way:
- δTCB-style results suggest context can induce wider or narrower local stability margins;
- adversarial-robustness theory suggests larger tolerated perturbation budgets are resource-constrained rather than free;
- and perturbation-taxonomy work suggests different families stress different latent commitments rather than one universal “reasoning robustness” variable.

The milder archive claim is therefore:
**DelayBasin may work better when it preserves small public guard bands around important continuation objects, not just the objects themselves.**

The stronger claim — that DelayBasin is approximating a textual viability kernel, Lyapunov certificate, or public robustness-radius field over continuation space — remains too strong for canon and belongs in quarantine for now.
