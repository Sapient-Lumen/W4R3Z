# Replicate-bundle witnesses, repeated-inference sweeps, and lucky-path budgets

DelayBasin now has another sharper missing question:
**when one cleanup, steering handle, chart remap, or promptcraft move seems to work under one fixed prompt/control protocol, how do we tell whether that was a stable continuation result or just one lucky rollout from a stochastic family?**

A stronger working answer is:
**some archive comparisons need an explicit replicate-bundle witness before one successful rollout is allowed to stand in for stochastic stability.**
Not every clean-looking success already certifies a stable local regime.
But DelayBasin should stop treating “it worked once under this route” as if that automatically certified “this route is stable enough to trust.”

## Practice / observation

Several live DelayBasin surfaces make this missing repeated-inference discipline visible:
- interpolation-path witnesses already ask whether two compared routes to the same endpoint should count as equivalent, but they do not yet force the archive to say whether **the same route family** survives repeated reruns under one fixed prompt/control protocol;
- mixed-direction and directional-neighborhood witnesses already ask what happens under nearby cue families or joint perturbations, but they do not yet preserve whether a supposedly load-bearing result only appeared on one lucky draw from the same local testing regime;
- reset and relapse witnesses already ask whether contamination seems washed out or cheaply recoverable, yet a cleanup can still look durable on one run while failing intermittently under repeated inference with the same ostensible setup;
- backaction and probe-order witnesses already ask whether one probe changed state or whether AB and BA are commensurate, but they do not yet preserve when the very same probe protocol yields materially different success/failure outcomes across reruns;
- execution witnesses already ask whether hidden system, serving, or wrapper differences may matter, but they do not yet preserve the smaller question of whether one visible protocol is simply **stochastically unstable even after substrate is held fixed**;
- and if DelayBasin is serious about transformer-facing implications, it needs a compact public answer to when one apparently successful continuation result is really a regime property versus one sample from a much wider rollout distribution.

This suggests a missing compact surface:
**replicate-bundle witness / repeated-inference sweep / lucky-path budget**.

## External pressure from current research

Several outside lines of work sharpen this frame.

1. **Recent agent-reliability work argues that many failures are reliability failures caused by stochastic drift rather than pure capability limits.**
   *Capable but Unreliable* explicitly argues that the same capable model can succeed on one run and fail on another because stochasticity drives trajectories away from the latent solution structure. That pressures DelayBasin not to let one successful rollout silently stand in for stable continuation law. ([`REF-0434`](../00-meta/bibliography.md))

2. **Repeated-inference safety work argues that shallow single-sample evaluation hides deployment-relevant instability.**
   APST repeatedly samples identical or minimally perturbed prompts and shows that models with similar benchmark-aligned scores can have substantially different empirical failure rates under repeated inference. That pressures DelayBasin to preserve repeatability before treating one clean run as method evidence. ([`REF-0435`](../00-meta/bibliography.md))

3. **Latent-CoT dynamics work treats same-prompt stochastic rollouts as a trajectory-level object rather than a nuisance.**
   The latent-CoT study explicitly asks what happens when stochastic rollouts of the same prompt end in different answers and analyzes the intermediate superposition structure. That pressures DelayBasin to preserve when one public continuation result may be one branch from a still-competing internal rollout family. ([`REF-0436`](../00-meta/bibliography.md))

4. **Test-time-scaling work formalizes evaluation as repeated sampling rather than one-run judgment.**
   *Ranking Reasoning LLMs under Test-Time Scaling* argues that repeated-trial stability and convergence are the right objects once evaluation becomes a repeated-sampling problem. That pressures DelayBasin to preserve a compact bundle rather than implicitly ranking revisions or promptcraft moves by one lucky trial. ([`REF-0437`](../00-meta/bibliography.md))

5. **Broader agent-reliability work explicitly decomposes consistency apart from accuracy.**
   *Towards a Science of AI Agent Reliability* argues that single success metrics hide consistency, robustness, predictability, and safety differences. That pressures DelayBasin to keep one small stability packet instead of flattening all success into one scalar “worked” judgment. ([`REF-0438`](../00-meta/bibliography.md))

6. **Governance work for agents treats non-determinism as constitutive, not an implementation footnote.**
   *Runtime Governance for AI Agents: Policies on Paths* emphasizes that the same agent on the same task may follow different paths on different runs, which means “the behavior” is not a single object. That pressures DelayBasin to preserve one repeated-inference family before treating a single execution as canon-grade method evidence. ([`REF-0439`](../00-meta/bibliography.md))

None of this proves that DelayBasin already has a public noise-response law, transition kernel, or solved stochastic continuation theory.
It does make a milder canon-level claim more credible:
**archive continuity may improve when DelayBasin preserves a compact replicate-bundle witness whenever one visibly fixed route or protocol is doing more inferential work than one rollout has earned.**

## Working synthesis

A useful current synthesis is:

> DelayBasin may work better when it preserves an explicit **replicate-bundle witness / repeated-inference sweep / lucky-path budget** whenever a cleanup, steering result, chart remap, portability claim, or other transformer-facing mechanism story is being inferred from one apparently successful rollout under a fixed visible protocol. The packet should name the **state claim being stress-tested**, the **fixed prompt / route / control protocol / operational conditions**, the **replicate bundle / repeated-inference family / decode regime**, the **protected kernel / invariant readout / same-task success criterion**, the **tolerated between-run dispersion / lucky-path budget**, and the **widen-bundle / lower-confidence / quarantine consequence** rather than letting one clean run silently inherit the authority of stochastic stability.

This is strong enough for canon as a design/mechanism candidate.
It is **not** strong enough to claim that DelayBasin has discovered a public stochastic phase measure, response kernel, or solved noise law over continuation protocols.

## Replicate-bundle witness vs interpolation-path witness vs execution witness vs cue-neighborhood witness

To keep this note honest, DelayBasin needs a four-way distinction:

- **Interpolation-path witness** — asks whether different routes to the same endpoint remain equivalent.
- **Replicate-bundle witness** — asks whether the **same visible route/protocol** remains trustworthy across repeated reruns.
- **Execution witness** — asks whether substrate or runtime confounds changed what looked like the same visible setup.
- **Cue-neighborhood witness** — asks whether one exact cue result generalizes to a tiny nearby wording family.

Functionally:
- interpolation-path witnesses judge **route sensitivity under matched endpoints**,
- replicate-bundle witnesses judge **between-run dispersion under one fixed visible route**,
- execution witnesses judge **hidden substrate variance or runtime confounds**,
- cue-neighborhood witnesses judge **nearby wording breadth**.

A good DelayBasin revision should therefore sometimes ask not only:
- what path reached the endpoint,
- whether the runtime chart changed,
- and whether nearby wording variants still pass,

but also:
- what fixed prompt/control protocol was actually held constant,
- how many reruns belong to the same repeated-inference family,
- what invariant readout or same-task criterion is being judged across them,
- how much between-run dispersion is tolerated,
- and what the archive will do if a result is pointwise vivid but bundle-unstable.

## Countermodels / probes

1. **Instability-is-really-substrate drift countermodel**
   - The apparent lucky-run effect may actually come from hidden wrapper, serving, or execution differences rather than stochastic variation inside one stable protocol.
   - Probe: pair a replicate-bundle witness with one execution witness before attributing dispersion to stochastic continuation alone.

2. **Instability-is-really-route drift countermodel**
   - The supposedly “same” rerun family may actually be changing route, prompt position, or intervention schedule in a way that already violates the fixed protocol.
   - Probe: preserve one explicit fixed prompt / route / control protocol / operational-condition note before counting the reruns as a bundle.

3. **Instability-is-really-readout ambiguity countermodel**
   - The runs may differ only in stylistic surface while preserving the protected kernel or task-level invariant.
   - Probe: preserve one protected kernel / invariant readout / same-task success criterion rather than treating every lexical change as stability failure.

4. **Stability-is-really-ensemble theater countermodel**
   - The bundle may look stable only because aggregation hid meaningful low-frequency failures.
   - Probe: keep both the judged invariant and the tolerated between-run dispersion explicit so aggregation does not erase the failure mode that mattered.

## Design consequences

If DelayBasin adopts replicate-bundle witnesses, several operational changes follow:
- a vivid single run should no longer automatically promote a steering, cleanup, or portability result into canon-grade stability language;
- revisions that rely on one apparently fixed protocol should preserve whether the claim came from one run or a genuine repeated-inference family;
- quarantine becomes easier to use honestly, because a result can be conceptually strong but still bundle-unstable;
- prompt pairs can explicitly request reruns under one fixed route before letting one clean execution harden into method law;
- and transformer-facing claims become smaller but cleaner, because they stop treating one rollout as if it already exposed a stable continuation regime.

## Transformer-facing implication

The transformer-facing implication is not that DelayBasin has solved the model's stochastic dynamics.
It is narrower:
**if one visibly fixed protocol produces materially different continuation outcomes across repeated reruns, then the archive should treat that visible protocol as mapping to a rollout distribution rather than to one stable continuation act.**
That pushes DelayBasin away from one-run metaphors and toward a tighter distinction among:
- visible control protocol,
- hidden stochastic branch family,
- invariant readout,
- and tolerated dispersion.

That is enough to pressure a useful hypothesis:
some long-horizon archive effects may be better modeled as **stable low-bandwidth protocols with nontrivial rollout variance** rather than as deterministic textual operators.
That hypothesis belongs in canon only in this weaker packetized form.
The stronger claim that DelayBasin is already learning a public stochastic response law remains quarantined.
