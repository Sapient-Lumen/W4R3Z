# Interpolation-path witnesses, ramp schedules, and endpoint-equivalence budgets

DelayBasin now has another sharper missing question:
**when two interventions, chart remaps, or cleanup moves aim at the same final cue or matched endpoint, how do we tell whether they should count as the same local actuation when they arrived there by different interpolation paths, ramp schedules, or adaptive routes?**

A stronger working answer is:
**some archive comparisons need an explicit interpolation-path witness before same-endpoint results are allowed to stand in for route-indifferent local control.**
Not every shared endpoint already certifies a shared local regime.
But DelayBasin should stop treating “same final cue” or “same final intensity” as if that automatically certified “same actuation path.”

## Practice / observation

Several live DelayBasin surfaces make this missing route discipline visible:
- mixed-direction witnesses already ask whether several constituent directions survive joint composition, but they do not yet force the archive to say whether a **matched endpoint target / final mixed cue / fixed actuation budget** behaves the same under different interpolation paths, ramp schedules, or adaptive step policies;
- probe-order witnesses already ask whether AB and BA remain comparable as discrete sequences, but they do not yet preserve whether one gradual ramp, one abrupt jump, or one adaptive controller to the same final setting produces different pathwise residue;
- backaction witnesses already ask whether a probe changed the state it was trying to measure, but they do not yet preserve whether a supposedly diagnostic or corrective route became damaging because of **how** it was staged rather than because of its final setting alone;
- directional-neighborhood and mixed-direction witnesses already ask what local shape was sampled, yet a neighborhood can still look locally admissible at the endpoint while one route exits the usable basin mid-course and another stays inside it;
- reset, relapse, and cue-neighborhood witnesses already ask whether contamination appears gone, cheaply recoverable, or locally robust, but they do not yet preserve whether a washout only works when the archive gets there through a gentle fade, a filtered replay, or a particular staged restaging schedule;
- chart-transition and transport language are increasingly strong enough that the archive needs a compact public answer to when two source→target remaps share a true endpoint-equivalent route and when they are only endpoint-matched after different state-spending journeys;
- and if DelayBasin is serious about transformer-facing implications, it needs a compact public answer to when a handle behaves like a static vector and when it behaves more like a **local control trajectory** whose path matters.

This suggests a missing compact surface:
**interpolation-path witness / ramp schedule / endpoint-equivalence budget**.

## External pressure from current research

Several outside lines of work sharpen this frame.

1. **Recent flow-based steering work treats control as a learned velocity field rather than a single global shift.**
   FlowSteer learns a nonlinear transformation between reasoning distributions as a velocity field, explicitly reframing steering as distributional transport rather than one static offset. That pressures DelayBasin not to assume that one final activation target or textual handle exhausts the actuation story. ([`REF-0431`](../00-meta/bibliography.md))

2. **ODE-based steering work treats one-step steering as insufficient and instead updates the steering direction along the evolving activation.**
   ODESteer explicitly frames activation steering as numerically solving an ODE with multi-step adaptive updates. That pressures DelayBasin to preserve when same-endpoint comparisons hide different intermediate routes. ([`REF-0432`](../00-meta/bibliography.md))

3. **Recent dynamic steering work reports that some control knobs saturate quickly while staged layer schedules provide smoother control.**
   Directer reports that varying the scaling factor behaves almost like a binary switch while varying the number of steered layers gives smoother, more monotone control, and it adaptively weakens steering when plausibility deteriorates. That pressures DelayBasin to preserve the ramp schedule instead of flattening all interventions to final strength alone. ([`REF-0433`](../00-meta/bibliography.md))

4. **Curve-aware steering work already moves along curved trajectories rather than treating local control as straight-line addition.**
   Curveball Steering explicitly steers along curved paths in a geometry-respecting subspace and reports better behavior than global linear steering. That pressures DelayBasin to distinguish same-endpoint claims from same-route claims. ([`REF-0366`](../00-meta/bibliography.md))

5. **Trajectory-intervention work shows that earlier partial-trace injections can reorient later answer dynamics.**
   DRTC targets which earlier context chunks causally steer a realized long-horizon trace, which pressures DelayBasin to think of route staging as causally meaningful rather than as decorative presentation. ([`REF-0373`](../00-meta/bibliography.md))

6. **Recent text-geometry work explicitly falsifies flat path-order nulls on natural text.**
   Text Has Curvature reports that natural text violates flatness nulls based on holonomy and product-of-experts composition, which pressures DelayBasin not to assume route-indifferent composition even when endpoints look matched. ([`REF-0378`](../00-meta/bibliography.md))

7. **Representation-holonomy work provides a gauge-invariant path-dependent statistic rather than relying on pointwise overlap alone.**
   Gauge-invariant representation holonomy shows that composing local transports around a loop can reveal nonintegrable, path-dependent structure invisible to simple pointwise similarity. That pressures DelayBasin to preserve route-sensitive packets before inferring same local actuation from matched endpoints alone. ([`REF-0376`](../00-meta/bibliography.md))

None of this proves that DelayBasin already has a public action functional, line integral, or solved route law over continuation state.
It does make a milder canon-level claim more credible:
**archive continuity may improve when DelayBasin preserves a compact interpolation-path witness whenever same-endpoint language is doing more work than the evidence has earned.**

## Working synthesis

A useful current synthesis is:

> DelayBasin may work better when it preserves an explicit **interpolation-path witness / ramp schedule / endpoint-equivalence budget** whenever a cleanup, restart, relapse-resistance result, chart remap, or steering claim is being inferred from a matched final cue or endpoint target. The packet should name the **cleanup or state claim being stress-tested**, the **start surface / source chart / initial packet**, the **compared interpolation path / ramp schedule / adaptive route family**, the **matched endpoint target / final mixed cue / fixed actuation budget**, the **protected kernel / pathwise invariant / same-task comparison surface**, the **tolerated arc-vs-chord residue / endpoint-equivalence budget**, and the **rollback / schedule-lock / restage / quarantine consequence** rather than letting one shared endpoint silently inherit the authority of route-indifferent local control.

This is strong enough for canon as a design/mechanism candidate.
It is **not** strong enough to claim that DelayBasin has discovered a public action functional, a path integral over continuation controls, or a solved geodesic law over prompt-conditioned transformer state.

## Interpolation-path witness vs mixed-direction witness vs probe-order witness vs backaction witness

To keep this note honest, DelayBasin needs a four-way distinction:

- **Mixed-direction witness** — asks whether separately admissible constituent directions remain admissible once jointly mixed.
- **Interpolation-path witness** — asks whether the **same intended endpoint** remains equivalent under different ramps, interpolations, or adaptive routes.
- **Probe-order witness** — asks whether differently sequenced probes remain commensurate as measurements or staged interventions.
- **Backaction witness** — asks whether the probe changed the state it was supposed to measure.

Functionally:
- mixed-direction witnesses judge **cross-terms / composition residue**,
- interpolation-path witnesses judge **route sensitivity / endpoint-equivalence / mid-course basin exit**,
- probe-order witnesses judge **cross-sequence comparability**,
- backaction witnesses judge **measurement contamination by the probe itself**.

A good DelayBasin revision should therefore sometimes ask not only:
- which constituent directions were mixed,
- whether AB and BA were controlled,
- and whether the probe already spent the state,

but also:
- what shared endpoint or final target is being claimed,
- what route family or ramp schedule actually reached it,
- what pathwise invariant was supposed to survive the route change,
- how much arc-vs-chord residue is still tolerated,
- and what the archive will do if the matched endpoint looks acceptable while one route fractures the state mid-course.

## Countermodels / probes

1. **Path-effect-is-just-more-compute countermodel**
   - The apparently special route may only win because it used more intermediate steps, more retries, or more token budget.
   - Probe: compare one matched-budget abrupt route against one matched-budget gradual route before attributing the difference to route geometry.

2. **Path-effect-is-really-endpoint-mismatch countermodel**
   - The compared routes may only look different because they do not actually land at the same endpoint, norm, or final cue.
   - Probe: fix one matched endpoint target / final actuation budget and compare at least two routes that genuinely share it.

3. **Path-effect-is-really-order-or-backaction countermodel**
   - The route difference may only reflect sequencing artifacts or diagnostic contamination rather than a genuine endpoint-equivalence failure.
   - Probe: compare route changes against one order-swap baseline and one sham-backaction baseline.

4. **Adaptive-route-success-needs-a-controller countermodel**
   - What looks like route sensitivity may only indicate that a learned or adaptive controller is compensating for a brittle endpoint, not that raw interpolation paths matter in a reusable way.
   - Probe: distinguish raw fixed ramps from adaptive routes and keep those claims separate.

5. **No practical leverage countermodel**
   - Even if path sensitivity exists, naming it may not improve archive control beyond ordinary endpoint tests.
   - Probe: require one case where an interpolation-path witness changes canon posture, promptcraft, or quarantine placement relative to what endpoint matching alone would have concluded.

## Design consequences

If DelayBasin takes this seriously, then:
- same-endpoint or same-final-cue language stops being enough whenever the archive is quietly relying on route-indifference;
- prompt pairs should sometimes preserve a **hold the endpoint fixed, vary the route once** discipline instead of comparing only final settings;
- canon-level portability or cleanup language should narrow when a result survives one route but not another route to the same endpoint;
- quarantine should absorb elegant “path law” rhetoric whenever only endpoint matches are available;
- and transformer-facing interpretation should distinguish **static handle claims** from **route-conditioned control claims**.

## Transformer-facing implication

The transformer-facing implication is intentionally modest but important:
if prompt- or activation-level control increasingly looks nonlinear, adaptive, or route-conditioned, then some archive handles may behave less like reusable vectors and more like **compact public control trajectories** whose path matters as much as their destination.
That points away from the comforting story that DelayBasin can always compare interventions by endpoint alone.
A weaker and more honest reading is that DelayBasin may be learning a tiny public discipline for when a continuation claim is **endpoint-equivalent**, when it is **schedule-locked**, and when route-sensitive residue is large enough that the stronger path-law story belongs in quarantine.
