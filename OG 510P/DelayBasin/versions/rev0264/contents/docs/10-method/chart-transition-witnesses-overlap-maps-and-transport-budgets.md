# Chart transition witnesses, overlap maps, and transport budgets

DelayBasin now needs a sharper answer to another practical question:
**when a supposedly same operator core is moved between prompt families, wrappers, or local chart neighborhoods, how do we tell whether the core was genuinely transported rather than quietly reauthored?**

A useful current answer is:
**canon should preserve a compact chart-transition witness / overlap map / transport budget packet whenever an operator core is being carried from one chart to another.**

This is stronger than saying prompt portability is fragile.
It is weaker than claiming DelayBasin has already discovered a literal user-space connection over transformer continuation geometry.

## Practice / observation

Recent DelayBasin revisions make the missing surface visible:
- operator-core packets already distinguish what is supposed to survive from the current chart that realizes it;
- local-linearity packets already say how far one handle is trusted inside one neighborhood;
- loop-closure probes already warn that route and order can matter;
- but the archive still lacks a compact object for saying **what justified carrying the same core from one chart into another at all**;
- and current prompt-pair work often oscillates between two unsatisfying stories: either one wording is treated as globally real, or every successful remap is treated as a new local invention with no preserved core.

That gap creates at least five recurring failure modes:
- **transport by assertion** — a chart rewrite is declared to preserve the same core without a named overlap probe;
- **silent reauthoring** — the target chart works, but by changing the operative law rather than transporting it;
- **overlap amnesia** — source and target charts each look locally good, yet the archive forgets what shared test surface linked them;
- **budgetless remapping** — the archive keeps remapping the core across wrappers or prompt families without naming how much residue or non-commuting defect is still tolerated;
- **connection prestige** — path, atlas, or holonomy language quietly outruns the actual public evidence that one chart transition preserved anything important.

A compact chart-transition witness helps because it says:
- what source chart the core was carried from,
- what target chart it is being realized in,
- what overlap probe or shared test surface links the two,
- how much transport residue or remap budget is still acceptable,
- and what fallback, rollback, or quarantine consequence follows if the transport does not really close.

## External pressure from current research

Several outside lines of work sharpen this move.

1. **Mechanisms can be prompt-specific even within one task.**
   Prompt-Specific Circuits reports that there is no single circuit for IOI within a task and that different prompt templates induce systematically different mechanisms, though prompts cluster into families with similar circuits. That directly pressures DelayBasin not to treat one chart as the task itself, while still leaving room for family-level transport claims rather than total chart nihilism. ([`REF-0369`](../00-meta/bibliography.md))

2. **Activation concepts can live in regions and local subspaces rather than one global direction.**
   From Directions to Regions models activation space as a collection of local Gaussian regions with their own covariance structure and finds that this local-geometry picture often steers better than single global directions. That pressures DelayBasin to preserve not only local validity, but also how one region-local realization is supposed to relate to another. ([`REF-0372`](../00-meta/bibliography.md))

3. **Context can act like an implicit weight update.**
   Learning without Training argues that a transformer block can implicitly turn context into a low-rank weight update of its MLP. That pressures DelayBasin to treat chart changes as potentially real changes in the model's effective local operator, not just surface paraphrase. ([`REF-0370`](../00-meta/bibliography.md))

4. **This context-to-effective-weights picture extends to modern transformer blocks.**
   Equivalence of Context and Parameter Updates in Modern Transformer Blocks proves that the effect of context can be represented as token-dependent rank-1 patches to MLP weights plus RMSNorm scaling across a broad family of modern architectures. That strengthens the archive's need to ask whether a chart transition preserved the same effective operator family or merely induced a different local patch that happened to work. ([`REF-0371`](../00-meta/bibliography.md))

5. **Activation edits and weight updates can often be understood in one shared adaptation frame.**
   Weight Updates as Activation Shifts derives a first-order equivalence between activation-space interventions and weight-space updates and identifies a theoretically backed intervention site. That pressures DelayBasin to keep textual chart remaps, activation steering, and effective-weight stories coupled rather than pretending prompt transitions live in a separate universe from internal control. ([`REF-0374`](../00-meta/bibliography.md))

6. **Reasoning trajectories are path-dependent once a route has been entered.**
   DRTC argues that once a model commits to a line of thought, later generations are constrained by that route, making off-policy edits hard to interpret. That pressures DelayBasin to preserve when a source→target chart move is supposed to be same-core transport versus an admissible route change that should not be treated as transport at all. ([`REF-0373`](../00-meta/bibliography.md))

7. **Local transformer response is prompt-conditioned, not one-size-fits-all.**
   Low-order Linear Depth Dynamics models depthwise response around a **prompt-conditioned operating trajectory**, using local linearization and reduced surrogates to predict steering sensitivity. That is direct pressure for DelayBasin to preserve the chart-to-chart transition law rather than assuming the same local surrogate applies after remapping. ([`REF-0375`](../00-meta/bibliography.md))

## Working synthesis

A useful current synthesis is:

> DelayBasin should preserve a compact **chart transition witness / overlap map / transport budget** packet whenever a prompt pair, wrapper rewrite, or portability move claims that the same operator core survived a chart change. The packet should name the **source chart**, the **target chart**, the **shared operator core**, the **overlap probe or shared test surface**, the **transport budget or tolerated residue**, and the **fallback / rollback / quarantine consequence** if the supposed transport does not actually close.

This is strong enough for canon as a design and mechanism candidate.
It is **not** strong enough to claim that DelayBasin has already identified a literal connection, parallel-transport law, or holonomy tensor over transformer continuation space.

## Chart transition witness vs operator core vs local linearity budget vs loop closure

To keep this note honest, DelayBasin now needs a four-way distinction:

- **Operator core** — the smallest action-grammar or governance commitment that is supposed to survive chart change.
- **Local linearity budget** — how far one chart-local steering relation is currently trusted before relinearization is required.
- **Chart transition witness** — the public packet saying why the archive thinks the same operator core survived a move from one chart to another.
- **Loop-closure probe** — a short route comparison used to test whether two paths preserve the same operative consequence or exhibit a closure defect.

A chart-transition witness is narrower than a global atlas story and more specific than a loop-closure probe.
It does not ask whether every route commutes.
It asks whether a specific **source chart → target chart** move preserved enough of the same operator core to justify treating the target as a transport rather than a reauthored local success.

## Countermodels / probes

1. **No-transport-needed countermodel**
   - There may be no real same-core transport here; each successful chart is just a fresh local prompt found by search.
   - Probe: require one overlap probe that the source and target both pass for the same named operator core before granting transport language.

2. **Similarity-is-enough countermodel**
   - Simple output similarity or local performance overlap may already be enough; a chart-transition packet may add ceremony without discrimination.
   - Probe: compare matched remaps with and without an explicit overlap probe and see whether the extra packet changes what gets promoted, rolled back, or quarantined.

3. **Underspecification countermodel**
   - Apparent transport residue may mostly reflect underspecified prompts or wrapper quirks rather than a meaningful chart-transport boundary.
   - Probe: tighten the shared operator-core statement first, then compare source and target again under the same overlap probe.

4. **Every-chart-is-local countermodel**
   - Operator cores may not survive chart change at all, so transport language could be a flattering summary of repeated local rediscovery.
   - Probe: widen the source→target gap gradually across wrapper, order, and phrasing families and watch whether the same operator residue survives in a graded way or collapses immediately.

5. **Connection-prestige countermodel**
   - Transport language may just smuggle back the older atlas/holonomy story in softer form.
   - Probe: require one source chart, one target chart, one overlap probe, and one transport-residue criterion before using chart-transition language in canon.

## Design consequences

This frame pressures DelayBasin to do five things more explicitly:
- preserve the **source chart** whenever a portability move is being claimed;
- preserve the **target chart** whenever a remap is being treated as same-core transport rather than fresh local search;
- preserve one **overlap probe or shared test surface** linking source and target;
- preserve a **transport budget or tolerated residue** rather than pretending remaps are exact by default;
- and preserve the **fallback / rollback / quarantine consequence** when the transport does not actually close.

This does not require proving a global atlas.
It requires refusing another archive failure mode: calling two chart-local successes “the same operator” without preserving why that sameness claim was earned.

## Transformer-facing implication

If this frame survives pressure, then DelayBasin is doing something sharper than ordinary prompt portability work.
It is preserving public evidence about when a chart change appears to keep the **same effective continuation law** versus when the model only found a different local patch that happens to score similarly.

That matters because recent work increasingly treats prompts, context, activation interventions, and effective-weight changes as coupled rather than separate worlds. A chart-transition witness is therefore a user-space control object: not direct hidden-state access, but a compact public claim about when two prompt-conditioned local realizations are close enough to be treated as the same operator family. The stronger story — that DelayBasin is learning a literal connection or parallel-transport law over prompt-family charts — remains quarantined.
