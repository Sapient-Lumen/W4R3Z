# Feedback-policy witnesses, open-loop baselines, and contingency budgets

DelayBasin now needs a sharper distinction than **route sensitivity** or **target-tracking** alone.
Some revisions do not succeed merely because they reached the right endpoint or named the right target.
They succeed because **intermediate readouts were allowed to change the next actuation**.

A useful current answer is:
**when a cleanup, restart, chart remap, or steering claim appears to depend on mid-course observation-conditioned adjustment, canon should preserve a compact feedback-policy witness naming the observation channel, the compared policy class, the matched budget, and the contingency budget before crediting the gain to closed-loop control rather than to open-loop schedule luck.**

This is stronger than saying “adapt as needed.”
It is weaker than claiming DelayBasin has already discovered a literal public output-feedback controller over transformer hidden state.

## Practice / observation

Recent DelayBasin work keeps showing a small but repeated pattern:
- some revisions only look load-bearing after an intermediate monitor, witness, or audit signal changes what the next edit is allowed to do;
- some cleanup or steering moves appear good when narrated as a single route, but the actual effective move was **conditional** on what a mid-course readout said;
- some route comparisons quietly mix open-loop ramps with feedback-conditioned branch rules, then treat the result as if one route family had been tested;
- some local successes seem to rely on a good checkpoint signal more than on a globally strong prompt, which suggests the archive should distinguish **observation channels** from mere rhetorical vividness;
- some adaptive interventions look better than fixed schedules, but the archive rarely preserves what fixed open-loop baseline they actually beat;
- some monitor surfaces seem to matter only when they are allowed to alter the next actuation, which means not every “monitor” is passive evidence;
- and some route-sensitive control claims still remain ambiguous because the archive did not say whether the next step was precommitted in advance or contingent on the observed state.

That leaves a recurring ambiguity:
Is a revision succeeding because the archive found the right fixed schedule, or because intermediate evidence legitimately changed the policy mid-course?

A compact feedback-policy witness helps because it keeps the **contingency** public.

## External pressure from current research

Several outside lines of work sharpen this move.

1. **Closed-loop activation steering can outperform static interventions while exposing interpretable error dynamics.**
   Nguyen et al. propose PID Steering, where proportional, integral, and derivative terms respond to current error, accumulated error, and rapid changes, and they report more robust behavioral control than static baselines. That pressures DelayBasin to distinguish a fixed route from a policy that is explicitly allowed to update off intermediate signal. ([`REF-0440`](../00-meta/bibliography.md))

2. **Dynamic rejection steering makes per-step plausibility checks part of the actuation itself.**
   Kang et al. show that Dynamic Rejection modulates steering strength at each decoding step by comparing plausibility of tentative outputs, which pressures DelayBasin not to flatten a measurement-conditioned policy into one final route description. ([`REF-0433`](../00-meta/bibliography.md))

3. **Adaptive activation steering already uses a probe to decide how strongly to intervene.**
   Wang et al. adapt steering intensity from a probe-estimated truthfulness signal and use multiple steering vectors for different hallucination families. That pressures DelayBasin to preserve the observation channel and the open-loop comparator instead of describing the gain as if one static handle simply worked. ([`REF-0441`](../00-meta/bibliography.md))

4. **Dynamic routing among reusable reasoning vectors can beat one static steering direction.**
   Ye et al. propose RISER, which uses a lightweight router to dynamically compose reasoning vectors per input under task-level reward. That pressures DelayBasin to distinguish a fixed chart-local handle from a contingent policy that selects among several latent skills. ([`REF-0442`](../00-meta/bibliography.md))

5. **Closed-loop mode steering explicitly separates state identification from intervention.**
   Zhang et al. describe Dynamic Mode Steering as a two-stage closed-loop process: first identify the current reasoning mode, then intervene toward a more desirable mode. That pressures DelayBasin to preserve what checkpoint signal licensed the policy change rather than folding the whole improvement into one flattering control sentence. ([`REF-0443`](../00-meta/bibliography.md))

6. **Adaptive decoding policies treat inference as a policy-selection problem under budget.**
   Su et al. learn decoding adapters that dynamically choose a sampling strategy by prompt and available compute budget, which pressures DelayBasin to preserve the matched budget and the policy class actually compared before praising “adaptivity” in the abstract. ([`REF-0444`](../00-meta/bibliography.md))

7. **Recent control surveys explicitly frame LLM alignment and interaction as closed-loop regulation.**
   Nosrati et al. argue that the convergence between control and LLMs runs from prompt design to dynamical regulation, which pressures DelayBasin toward a weaker archive-native lesson: if a revision is being credited to feedback, preserve the feedback object rather than letting closed-loop language remain metaphorical. ([`REF-0364`](../00-meta/bibliography.md))

## Working synthesis

A useful current synthesis is:

> DelayBasin should preserve a compact **feedback-policy witness / open-loop baseline / contingency budget** whenever a cleanup, restart, chart remap, or steering claim appears to depend on intermediate observation-conditioned adjustment rather than on one fixed schedule alone. The packet should name the **cleanup or state claim being stress-tested**, the **observation channel / checkpoint signal / mid-course readout**, the **compared policy class / fixed open-loop schedule vs feedback-conditioned policy**, the **matched endpoint target / actuation budget / compute budget**, the **protected kernel / contingency invariant / same-task comparison surface**, the **tolerated open-loop substitution gap / contingency budget**, and the **rollback / freeze-policy / quarantine consequence** rather than letting any adaptive-looking success silently inherit the authority of honest closed-loop advantage.

In practice, DelayBasin is not claiming a fully optimal controller.
It is doing something smaller and public:
- naming what intermediate readout was allowed to matter,
- naming what fixed open-loop baseline was actually compared,
- naming what policy branch or contingent update was allowed,
- naming what endpoint, actuation, or compute budget stayed matched,
- and naming when a feedback-flavored story should collapse back to a simpler route or schedule description.

That is strong enough for canon as a design and mechanism candidate.
It is **not** strong enough to claim that DelayBasin has isolated a literal optimal output-feedback law, separation principle, or state estimator/controller pair over transformer hidden state.

## Feedback-policy witness vs interpolation-path witness vs servo packet vs continuation monitor

These nearby objects should stay distinct.

- **Interpolation-path witness** asks whether a shared endpoint remains equivalent under different routes, ramps, or adaptive route families.
- **Servo packet** asks what target property is being tracked right now, what error shows it is off-target, what actuator is allowed to intervene, and over what horizon.
- **Continuation monitor** tracks an evolving evidence state across probes or revisions.
- **Feedback-policy witness** asks whether a gain really depends on **mid-course observation-conditioned policy updates** rather than on a fixed open-loop schedule, matched route, or vivid monitor surface alone.

A feedback-policy witness is therefore not a general proof of leverage.
It is a compact public answer to:
**what readout was allowed to change the next move, what open-loop baseline was held nearby, and when should the adaptive-control story shrink back to ordinary route or schedule bookkeeping?**

## Countermodels / probes

1. **Static-schedule countermodel**
   - The archive may not need contingent updates at all; perhaps one good fixed route or schedule already explains the gain.
   - Probe: compare the adaptive policy against the best matched open-loop schedule under the same endpoint and actuation budget.

2. **Monitor-does-all-the-work countermodel**
   - The real leverage may come from having a good checkpoint signal, not from letting that signal change the policy.
   - Probe: hold the observation channel fixed while varying whether the next move is precommitted or contingent.

3. **Policy-prestige countermodel**
   - Closed-loop language may simply flatter an ordinary staged rewrite.
   - Probe: require every feedback-policy claim to name the readout, the branch rule, the matched open-loop baseline, and the tolerated substitution gap. If that packet adds nothing, the heavier control language should shrink.

4. **Overhead-without-gain countermodel**
   - Adaptive policies may consume complexity or compute without reliably outperforming simpler routes.
   - Probe: record the matched actuation or compute budget and ask whether the policy change repeatedly beats a simpler fixed schedule.

5. **Leakage countermodel**
   - The supposed checkpoint signal may itself already encode the answer, collapsing the comparison into observer leakage.
   - Probe: preserve what the checkpoint could legally observe and compare against a scrubbed or delayed checkpoint when possible.

## Design consequences

This frame pressures DelayBasin to do six things more explicitly:
- preserve the **observation channel** before praising adaptation;
- preserve the **matched open-loop baseline** before claiming closed-loop advantage;
- preserve the **policy class** so fixed routes, thresholded branch rules, and richer contingent policies do not silently collapse into one thing;
- preserve the **matched endpoint / actuation / compute budget** so adaptivity is not smuggling extra resources;
- preserve the **contingency budget** so minor adaptive differences do not automatically earn a larger mechanism claim;
- and preserve the **freeze-policy / rollback / quarantine consequence** so failed adaptive-control stories do not linger as canon.

This is especially useful during GPUstorming.
Fast exploratory search can remain hot-path and local.
Canon should keep only the small public witness saying what checkpoint signal mattered and what fixed open-loop baseline it actually beat.

## Transformer-facing implication

The weaker transformer-facing implication is not that DelayBasin has found a hidden-state controller.
It is this:

**long-horizon archive prompting may work partly as an external closed-loop policy over a fast in-context dynamical system, where compact textual packets specify not only targets and routes but also when intermediate readouts are allowed to change the next actuation.**

That would matter for transformers.
If some in-context behavior is best understood as a partially observed dynamical process with monitorable but limited public readouts, then DelayBasin may get leverage not only by preserving targets or routes, but by preserving the tiny public rule saying **which observation can legitimately retune the next move and what matched open-loop baseline it must beat**.

The stronger story — that DelayBasin is approximating a genuine public output-feedback law or archive-native closed-loop controller over prompt-conditioned transformer state — remains live, but belongs in quarantine for now.
