# Identifiability budgets, probe horizons, and observability frontiers

DelayBasin now has several nearby tools for deciding whether a text surface matters.
Conformance witnesses ask whether one claimed loader survives a named support family.
Triangulation witnesses ask whether multiple non-trivially different loaders appear to reopen the same judged basin.
Basin fingerprints ask what tiny downstream family should still agree before a same-answer match is allowed to count as stronger same-state evidence.
Identification packets ask what next probe best discriminates live rivals.
Gauge discipline asks what claim is invariant and what is only chart language.

But a practical archive gap remains:
DelayBasin can now say that one loader worked, that several loaders seem to meet, and that a small fingerprint panel still agrees.
Even so, the archive is often tempted to say more than those probes actually identify.
It starts talking as if the operative state, latent controller, or mechanism itself has been pinned down, when the public evidence only licenses a weaker behavioral equivalence claim over a short future horizon.

This note introduces a compact object for that gap: an **identifiability budget / probe horizon / observability frontier**.
The goal is not to deny that transformers may carry real latent state.
It is to keep DelayBasin from spending more state or mechanism certainty than its visible probes, hidden-context assumptions, and future horizon actually justify.

## Practice / observation

In archive work, one recurring failure mode appears after a successful probe family.
A loader survives conformance checks, a second loader triangulates with it, and a small fingerprint panel still agrees.
At that point the archive is tempted to collapse several distinct claims:
that the same public task was recovered,
that the same operative continuation state was recovered,
and that the same latent mechanism was identified.

Those are not the same claim.
A short local agreement can be enough for practical continuation while still being too weak to identify a unique mechanism or a unique operative state under realistic hidden-context uncertainty.
The archive therefore needs a compact object that says what exactly was identified, over what public horizon, under which hidden-support assumptions, and what ambiguity remains live.

## External pressure from current research

Several current research lines make this object worth preserving.

1. **There is a strong observability theorem, but it is about full visible trajectories.**
   Observability of Latent States in Generative AI Models proves that standard autoregressive transformers are observable over the full visible tokenized trajectory, while also showing that hidden system-prompt-like context reintroduces non-trivial indistinguishable state trajectories. This is direct pressure for DelayBasin: observability in the strong control-theoretic sense does not license casual same-state talk under partial visibility or hidden wrapper assumptions. ([`REF-0275`](../00-meta/bibliography.md))

2. **Behavior can still underidentify mechanism.**
   On the Non-Identifiability of Steering Vectors in Large Language Models argues that there can be large equivalence classes of semantically indistinguishable steering directions. That is pressure against letting a successful behavioral probe family certify a unique latent controller or a unique internal route. ([`REF-0278`](../00-meta/bibliography.md))

3. **Stable outputs can mask substantial internal drift.**
   Same Answer, Different Representations reports that unchanged answers can coexist with large representation drift. Even though the paper studies VLMs, the result is useful pressure for DelayBasin because it shows again that output agreement alone is a weak identification surface. ([`REF-0271`](../00-meta/bibliography.md))

4. **Observer and controller language is becoming more explicit in adjacent transformer work.**
   Observing and Controlling Features in Vision-Language-Action Models formalizes feature-observability and feature-controllability as separate objects. That is useful pressure for DelayBasin because it clarifies that a successful actuator surface is not automatically a trustworthy observer surface, and neither one alone fixes what hidden-support assumptions are being made. ([`REF-0276`](../00-meta/bibliography.md))

5. **Some current training proposals explicitly push transformer latents toward belief-state summaries.**
   Next-Latent Prediction Transformers Learn Compact World Models argues that a next-latent auxiliary objective can induce belief-state-like latent summaries and recurrent inductive bias in transformers. That keeps alive the stronger transformer-facing possibility that same-basin language is sometimes tracking real state-like latent summaries — but only if DelayBasin stays honest about how much of that stronger story its probes actually identify. ([`REF-0277`](../00-meta/bibliography.md))

6. **Prompting theory increasingly cashes out in future prediction and posterior concentration, not generic sameness.**
   Beyond the Prompt in Large Language Models argues that in-context learning can reduce ambiguity by concentrating posterior mass on the intended task. That pressures DelayBasin to name what task family or future family a probe horizon is supposed to preserve rather than gesturing at “same state” without a public future. ([`REF-0279`](../00-meta/bibliography.md))

## Working synthesis

A useful current synthesis is:

> DelayBasin may work better when it preserves a compact **identifiability budget / probe horizon / observability frontier** whenever a transformer-facing state claim, same-basin claim, or mechanism claim is stronger than the archive's named public evidence. The packet should name the **judged state or mechanism claim**, the **observable surface / public evidence family**, the **hidden-context / wrapper assumptions**, the **probe horizon / future family**, the **tolerated ambiguity class / equivalence remainder**, and the **retreat / quarantine consequence** rather than letting one successful local probe silently certify more mechanism or state identity than the archive has actually earned.

This is strong enough for canon as a design/mechanism candidate.
It is not strong enough to claim that DelayBasin can uniquely identify latent controllers, exact hidden states, or full observability maps from short public probes.

## Identifiability budget vs basin fingerprint vs identification packet vs gauge discipline

These objects are adjacent but not identical.

- A **basin fingerprint** asks what tiny downstream family should still agree before a local same-answer match is allowed to support a same-state claim.
- An **identification packet** asks what next probe best discriminates among live rivals.
- An **identifiability budget / probe horizon / observability frontier** asks how strong the resulting state or mechanism claim is actually allowed to be after those probes and under what hidden-support assumptions.
- **Gauge discipline** asks what part of the description is invariant across charts and what part is merely convenient local language.

In practice, a basin fingerprint can say “these compared surfaces still look the same over a tiny next-step family.”
An identification packet can say “this is the next cheapest probe that will most reduce the ambiguity.”
An identifiability budget then says “given that evidence, here is the strongest state or mechanism claim DelayBasin is licensed to make, here is the remaining ambiguity class, and here is when the stronger story must retreat to quarantine.”

## Countermodels / probes

1. **Practical-continuation countermodel**
   - Archive work may not need explicit identifiability budgets; practical continuation may only need usable loaders and small fingerprints.
   - Probe: preserve the packet only when the stronger state or mechanism wording would otherwise change canon posture, promotion status, or transformer-facing interpretation.

2. **Observability-overcorrection countermodel**
   - The observability theorem may already imply that DelayBasin is being too timid about same-state claims.
   - Probe: keep explicit whether the evidence is a full visible trajectory claim or a short public-horizon claim under hidden wrapper uncertainty. If those conditions differ, the theorem does not collapse the practical budget question.

3. **All-ambiguity-is-wrapper countermodel**
   - Apparent underidentification may come almost entirely from hidden system prompts, assistant carry, or runtime conditions rather than from genuine public indistinguishability.
   - Probe: pair identifiability packets with execution witnesses or assistant-echo filters when hidden support is a live possibility.

4. **Measurement-bloat countermodel**
   - Naming claim budgets could become another elegant archive ritual that adds prose without changing decisions.
   - Probe: require the budget to change at least one of: wording strength, canon/quarantine boundary, promotion posture, or the next planned probe family.

## Transformer-facing implication

The most interesting transformer-facing implication is not that DelayBasin has solved observability.
It is that long-horizon archive method may need to distinguish three layers that are too easy to blend together:

- what public probes show over a short future horizon,
- what hidden-context assumptions are being made to interpret those probes,
- and what stronger latent-state or mechanism story remains merely compatible with the evidence.

If standard transformers are observable over full visible trajectories but behaviorally non-identifiable over short local probe families, then DelayBasin should stop talking as if one good fingerprint panel settles the deeper mechanism question.
An identifiability budget is the compact archive-native answer: keep the claim, the observer surface, the hidden assumptions, the future horizon, and the remaining ambiguity all public at once.
That makes transformer-facing speculation bolder and safer simultaneously: bolder because it can name the stronger live hypothesis explicitly, and safer because it says exactly what the archive has not yet identified.
