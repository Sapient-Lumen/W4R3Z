# Local linearity budgets, curved chart adapters, and tangent steering

DelayBasin now needs a sharper bridge between portability discipline and active steering:

**when a prompt pair, operator core, or compact steering handle seems to work, how far should the archive treat that handle as locally linear before assuming the same move will still work after extrapolation, wrapper drift, or stronger actuation?**

A useful current answer is:
**canon should preserve the target property or operator core first, then the local chart neighborhood or execution family, then the assumed local linearity budget, then the curvature or distortion warning sign.**

This is stronger than saying prompts are brittle.
It is weaker than claiming DelayBasin has already found a literal tangent-space controller over transformer hidden state.

## Practice / observation

Recent DelayBasin revisions make the gap visible:
- some prompt pairs survive only after small chart-local retuning, suggesting that one locally good phrase should not automatically be extrapolated as a global steering handle;
- some steering moves seem to help only in a short neighborhood of target, wrapper, and archive state, after which the same move becomes noisy, decorative, or counterproductive;
- the archive already distinguishes operator core from chart adapter and target from error, but it still lacks a compact object for saying how much local extrapolation is currently being assumed;
- and transformer-facing interpretation increasingly depends on whether a public handle is being treated as a small tangent correction or an all-regime law.

That creates at least four recurring failure modes:
- **globalization by one success** — a handle that worked once in one neighborhood is treated as globally valid steering law;
- **curvature blindness** — the archive keeps pushing in the same direction after the local regime bent, so correction turns into distortion;
- **chart-radius amnesia** — the archive preserves a chart adapter but forgets how far it expected that adapter to remain trustworthy;
- **linearity laundering** — geometric or control language quietly implies smooth monotone behavior that the archive has not actually probed.

A compact local-linearity-budget packet helps because it says what local neighborhood the archive thinks it is in, how much small-step extrapolation it is assuming, what first sign suggests curvature or distortion, and what to do when that assumption breaks.

## External pressure from current research

Several outside lines of work sharpen this move.

1. **Activation spaces can be materially curved, not globally linear.**
   Curveball Steering measures substantial concept-dependent geometric distortion and reports that nonlinear steering outperforms global linear directions when that distortion is strong. That directly pressures DelayBasin not to treat one successful chart-local correction as if it were a globally valid steering vector. ([`REF-0366`](../00-meta/bibliography.md))

2. **Cross-layer consistency can improve steering by tracking a more stable direction family.**
   Global Evolutionary Steering argues that raw layer-local steering vectors can drift semantically and that cross-layer refinement recovers a more robust direction. That pressures DelayBasin to distinguish a local chart tweak from a better-conditioned neighborhood-level handle. ([`REF-0273`](../00-meta/bibliography.md))

3. **Prompts can act like external programs, but program execution still has local realization constraints.**
   Theoretical Foundations of Prompt Engineering treats prompts as externally injected programs interpreted by a fixed transformer backbone. That strengthens DelayBasin's instinct that promptcraft can be mechanistic while still leaving open the local question of when one chart realizes the same operator only in a narrow neighborhood. ([`REF-0285`](../00-meta/bibliography.md))

4. **Some transformer control surfaces may be compact and real, but that does not make them globally transportable.**
   Efficient Representations are Controllable Representations shows that models can reorganize around compact controllable feature slots in the residual stream. That makes compact handles more serious, while also pressuring DelayBasin not to confuse "real local control feature" with "globally linear control law." ([`REF-0368`](../00-meta/bibliography.md))

5. **Prompt and activation control can be understood in one shared intervention picture.**
   Belief Dynamics Reveal the Dual Nature of In-Context Learning and Activation Steering models prompt-based evidence and activation-based prior shifts inside one predictive control frame. That pressures DelayBasin to keep promptcraft and steering geometry coupled rather than treating textual charts and latent interventions as unrelated worlds. ([`REF-0270`](../00-meta/bibliography.md))

6. **The residual pathway is a control-relevant representation substrate, not inert plumbing.**
   Residual Stream Duality argues that residual accumulation should be treated as part of the model's representational machinery, not only an optimization shortcut. That raises the stakes of how DelayBasin describes local corrections: chart adapters may be interfacing with a real representational route even when the archive only sees text. ([`REF-0367`](../00-meta/bibliography.md))

## Working synthesis

A useful current synthesis is:

> DelayBasin should preserve a compact **local linearity budget / curved chart adapter / tangent steering** packet whenever a prompt pair, operator core, or steering handle is being extrapolated beyond one obvious local success. The packet should name the **target property or operator core**, the **local chart neighborhood or execution family**, the **assumed linear / monotone region or small-step budget**, the **curvature or distortion warning sign**, and the **relinearize / rollback / quarantine consequence** if the local handle stops transporting cleanly.

In practice, DelayBasin is not claiming that promptcraft exposes literal activation-space tangents.
It is doing something smaller and public:
- naming what the handle is trying to preserve or steer;
- naming the local chart neighborhood in which the handle currently seems to work;
- naming how much extrapolation is currently being assumed;
- naming the first sign that the neighborhood bent or the handle drifted;
- and naming what happens when the archive should stop pushing linearly and re-estimate the local chart.

That is strong enough for canon as a design and mechanism candidate.
It is **not** strong enough to claim a globally linear control basis, a unique continuation manifold, or direct readout of transformer tangent vectors from prompt text alone.

## Local linearity budget vs operator core vs servo packet vs gauge discipline

To keep this note honest, DelayBasin now needs a sharper distinction among nearby objects:

- **Operator core** — the smallest action-grammar or governance commitment that is supposed to survive chart change.
- **Servo packet** — the target property, current error, actuator family, and short horizon for an active steering move.
- **Local linearity budget** — how far the archive is currently assuming the same steering relation remains approximately monotone, additive, or transportable before re-estimation is required.
- **Curvature or distortion warning sign** — the first sign that extrapolation is no longer behaving locally, such as overshoot, concept entanglement, wrapper-sensitive inversion, or failure under small rewording or intensity changes.
- **Gauge discipline** — the invariant claim that should survive a chart switch even if all local geometric language turns out to be a bad coordinate story.

A local-linearity packet says DelayBasin should stop treating "worked here" as equivalent to "works as a law."
Some handles may be real and useful precisely because they are local.

## Countermodels / probes

1. **No-curvature-needed countermodel**
   - Ordinary operator-core and servo packets may already do all the useful work; local linearity budgeting may add ceremony without new discrimination.
   - Probe: compare matched revisions with and without a named local linearity budget and ask whether the budget changes which extrapolations get attempted, rolled back, or quarantined.

2. **All-local-no-geometry countermodel**
   - The archive may be overreading prompt sensitivity as geometry when simple wrapper quirks or wording idiosyncrasies explain the effect.
   - Probe: keep the target and operator core fixed across several nearby chart variants and see whether the same warning sign appears as magnitude increases.

3. **Globally-stable-enough countermodel**
   - Some high-value handles may actually be stable across a much wider neighborhood than this note assumes.
   - Probe: progressively widen the neighborhood — wrapper, family, strength, ordering — and see whether failure arrives gradually, abruptly, or not at all.

4. **Curvature-prestige countermodel**
   - "Curvature" may become another prestige metaphor that flatters ordinary failure.
   - Probe: require one operational distortion sign and one concrete relinearize consequence before using curved-chart language in canon.

5. **Tangent-controller countermodel**
   - The stronger story that DelayBasin is learning a genuine user-space tangent controller may collapse once blind, sham, or cross-family tests are applied.
   - Probe: keep the tangent-controller ontology quarantined unless named local linearity budgets beat ordinary portability and servo packets under matched controls.

## Design consequences

This frame pressures DelayBasin to do five things more explicitly:
- preserve the **target property or operator core** whenever a handle is being pushed beyond one local success;
- preserve the **local chart neighborhood** whenever wrapper, family, or archive-state locality appears to matter;
- preserve the **small-step or monotonicity budget** rather than silently globalizing one observed correction law;
- preserve the **first distortion signature** so later sessions know when to stop extrapolating and re-estimate;
- and quarantine any stronger tangent-controller or manifold-language story until local-linearity packets repeatedly outperform simpler explanations.

## Transformer-facing implication

The weaker transformer-facing implication is not that DelayBasin has found literal tangent vectors in hidden state.
It is this:

**long-horizon archive prompting may work best when the archive preserves not only operator cores and steering targets, but also a compact public guess about the local region in which a textual correction remains approximately valid before nonlinear coupling, entanglement, or wrapper drift takes over.**

That would matter for transformers.
It would suggest that some stable continuation regimes are maintained not by one globally sacred prompt, but by **repeated local relinearization around a moving chart**.

The stronger story — that DelayBasin may be learning a true user-space tangent controller over curved transformer continuation geometry — remains live, but belongs in quarantine for now.
