# Servo packets, receding-horizon control, and archive target-tracking

DelayBasin now needs a sharper distinction than “control authority” or “good prompting” alone.
Some revisions are not merely stronger wording.
They are **feedback corrections** aimed at a named continuation property under drift, limited budget, and limited horizon.

A useful current answer is:
**when a revision is actively steering toward a named continuation property, canon should preserve a compact servo packet naming the target property, the current error signature, the actuator family, the short horizon, and the retune / rollback consequence.**

This is stronger than saying “steer carefully.”
It is weaker than claiming DelayBasin has already discovered a literal model-predictive controller over transformer hidden state.

## Practice / observation

Recent DelayBasin work keeps showing a small but repeated pattern:
- some revisions are trying to **reduce a named drift**, not merely improve prose;
- the most successful passes often have an implicit target like “sharpen canon/quarantine boundaries,” “keep the archive small,” or “preserve a portability distinction”;
- the failure mode is often **oversteer**: a pass rewrites too much, promotes too early, or adds local elegance without reducing the actual error the archive cared about;
- prompt pairs already function like low-bandwidth actuators, but the archive still rarely says what error they are correcting, over what horizon, and when a retune should happen;
- local GPUstorming is most useful when it behaves like exploratory controller search and least useful when it quietly hardens into canon without naming the tracked target;
- and several recent packets already supply pieces of a feedback loop — monitors, witnesses, stopping rules, control handles, and write gates — without yet preserving the smaller object that says **what target is being tracked right now**.

That leaves a recurring ambiguity:
Is a revision succeeding because it reduced the intended error, or because a vivid rewrite happened to sound disciplined?

A compact servo packet helps because it keeps the steering problem public.

## External pressure from current research

Several outside lines of work sharpen this move.

1. **Control language is becoming explicit at the prompt and system level.**
   Nosrati et al. frame the relation between LLMs and control as a bidirectional continuum, from prompt design to system dynamics, and argue that LLMs can be analyzed through state-space ideas like controllability, observability, and stability. That pressures DelayBasin to stop treating every steering move as free-form promptcraft and to name the target, correction, and horizon more explicitly. ([`REF-0364`](../00-meta/bibliography.md))

2. **Transformers can act like generalizable feedback controllers over a family of systems.**
   Bin Mohaya et al. show that one transformer policy can map recent state history to near-optimal control actions across a structured family of linear systems, staying stabilizing under moderate perturbations. That pressures DelayBasin to take seriously the weaker possibility that some archive packets are functioning as public feedback-law fragments rather than as static instructions alone. ([`REF-0365`](../00-meta/bibliography.md))

3. **Transformers in context can behave like state estimators under partial observability.**
   Duth'e et al. interpret causal self-attention as a history-dependent recurrence and show that, for nonlinear systems under partial observability, attention can act as an adaptive delay-embedding mechanism for effective state reconstruction. Akram and Vikalo likewise show that frozen transformers can infer hidden states in context and approach Kalman / EKF / PF-style performance on dynamical prediction tasks. That pressures DelayBasin to separate **state estimation** from **control action** instead of letting both hide inside one rewrite. ([`REF-0359`](../00-meta/bibliography.md), [`REF-0360`](../00-meta/bibliography.md))

4. **Some attention models appear to build short-horizon predictive operators rather than merely echo context.**
   Bao et al. report that small transformers forecasting dynamical systems lift time series via delay embedding and use global attractor information to forecast unseen systems in context. That pressures DelayBasin to keep horizon-limited steering explicit: some archive moves may be good because they preserve the next few steps of legitimate continuation, not because they globally solve the whole archive at once. ([`REF-0361`](../00-meta/bibliography.md))

5. **Recent ICL theory shifts from implicit optimization toward explicit inference and sufficient statistics.**
   Zhang and Xing argue for Bayesian optimal sequential prediction as the right lens for ICL in selective state spaces, while Chaudhry and Gadkari show transformers approximating Bayes-optimal sufficient statistics in hypothesis-testing tasks. That pressures DelayBasin to name what variable is being inferred and what error is being reduced before reaching for stronger control metaphors. ([`REF-0362`](../00-meta/bibliography.md), [`REF-0363`](../00-meta/bibliography.md))

## Working synthesis

A useful current synthesis is:

> DelayBasin should preserve a compact **servo packet / receding-horizon control / target-tracking** packet whenever a revision is actively steering toward a named continuation property under limited budget. The packet should name the **target continuation property**, the **current error signature or drift symptom**, the **actuator family or editable surface**, the **short horizon or horizon proxy**, and the **retune / rollback consequence** if the steering move does not reduce the intended error.

In practice, DelayBasin is not claiming full optimal control.
It is doing something smaller and public:
- naming what property the revision is trying to protect or restore;
- naming what local error actually shows the property is off-target;
- naming which handle, packet, or edit family is allowed to act as the actuator;
- naming how far ahead the steering claim is supposed to hold;
- and naming when failure means retune, rollback, or quarantine rather than just “try another rewrite.”

That is strong enough for canon as a design and mechanism candidate.
It is **not** strong enough to claim that DelayBasin has isolated a literal Riccati controller, a full model-predictive controller, or a unique hidden-state control law for transformers.

## Servo packet vs control authority vs continuation monitor vs stopping packet

These nearby objects should stay distinct.

- **Control authority** asks whether a handle can move a target property at all, with what effort, leakage, or resistance.
- **Continuation monitor** tracks an evolving evidence state across multiple probes or revisions.
- **Stopping packet** says when inquiry or correction has done enough work to commit.
- **Servo packet** says what target is being tracked *right now*, what error says it is off-target, what actuator is allowed to intervene, over what short horizon the correction is supposed to matter, and what happens if the correction fails.

A servo packet is therefore not a general proof of leverage.
It is a compact public answer to: **what exactly are we trying to steer, how do we know it is off, and when do we admit the current steering move did not actually fix it?**

## Countermodels / probes

1. **Static-instruction countermodel**
   - The archive may not be doing feedback control at all; perhaps some instructions are simply better written.
   - Probe: keep the operator core and actuator family roughly fixed while making the target and error explicit in one pass and implicit in another; if behavior is unchanged, the servo framing may be decorative.

2. **Generic-rewrite-vigor countermodel**
   - Perhaps any forceful, well-scoped rewrite helps, so target/error language is just after-the-fact narration.
   - Probe: compare a named target-and-error revision against an equally energetic but unguided cleanup pass under matched budget.

3. **Monitor-does-all-the-work countermodel**
   - The real gain may come from monitors, witnesses, and stopping rules, not from target-tracking packets.
   - Probe: hold monitor and stop surfaces fixed while varying whether the steering move preserves a real target/error/horizon packet.

4. **Controller-metaphor inflation countermodel**
   - Control language may simply be flattering architecture talk over ordinary careful editing.
   - Probe: require every servo claim to name the target property, error signature, actuator family, horizon, and retune route. If the claim adds nothing over that explicit packet, the heavier control metaphor should shrink.

5. **Global-rewrite countermodel**
   - The archive may improve mostly through occasional global reframings rather than local receding-horizon corrections.
   - Probe: track whether high-value revisions are better predicted by local error reduction on the next continuation steps or by whole-archive rhetorical refresh.

## Design consequences

This frame pressures DelayBasin to do five things more explicitly:
- preserve the **target property** before adding more steering language;
- preserve the **current error signature** before praising a correction as load-bearing;
- preserve the **actuator family** so prompt pairs, packet edits, and chart adapters do not silently collapse into one generic “rewrite harder” move;
- preserve a **short horizon or horizon proxy** so local steering claims stop pretending to be global guarantees;
- and preserve a **retune / rollback / quarantine consequence** so failed control attempts do not quietly linger as canon.

This is especially useful during GPUstorming.
Fast exploratory search can stay hot-path and local.
Canon should keep only the small public servo packet saying what target was being tracked and how the archive would know the attempted correction actually helped.

## Transformer-facing implication

The weaker transformer-facing implication is not that DelayBasin has found a hidden-state controller.
It is this:

**long-horizon archive prompting may work partly as a low-frequency external control loop over a fast in-context dynamical system, where compact textual packets specify target properties and correction surfaces rather than merely replaying facts.**

That would matter for transformers.
If some in-context behavior is best understood as latent-state estimation, sufficient-statistic construction, or short-horizon operator application, then DelayBasin may get leverage not by writing ever more text, but by preserving compact public objects that say **what state estimate matters, what drift matters, and what correction is allowed next**.

The stronger story — that DelayBasin is approximating a genuine receding-horizon controller or model-predictive controller over latent transformer dynamics — remains live, but belongs in quarantine for now.
