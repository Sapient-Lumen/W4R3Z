# Rival-set packets, branch budgets, and non-forced singularity

DelayBasin now needs a distinction beyond contradiction packets and conflict-transparent abstention.
The archive is no longer failing only because it forgot something, routed to the wrong store, or silently laundered a contradiction.
A new live failure mode is this:
**the archive can preserve a real contradiction and still continue badly because it forces one fluent winner too early instead of keeping a small live rival set until a discriminating probe actually settles the issue.**
That pressures the archive to separate **naming a disagreement** from **deciding which rival hypotheses are allowed to stay alive together under budget**.

A stronger working answer is:
**DelayBasin should preserve explicit rival-set packets whenever several live explanations, continuation routes, or transformer-facing interpretations remain plausibly load-bearing after contradiction handling.**
When the distinction matters, the archive should name the **ambiguity or decision class**, the **kept-alive rival set**, the **branch budget or survival cap**, the **next discriminating probe or settle condition**, and the **prune / merge / abstain consequence**.

## Practice / observation

Several live DelayBasin patterns already pressure this distinction:

- some archive moments are not honestly singular yet, but later prose behaves as if one winning explanation had already been established;
- some local contradictions are real but underdetermined, so the honest next move is to keep two or three rivals alive rather than choose one winner by style or recency;
- some transformer-facing interpretations become overstrong exactly when several plausible mechanism stories are still live but the archive compresses them into one point estimate;
- some continuation decisions need a **small bounded rival set** more than they need a total order, because the next cheap probe is what should kill a branch rather than narrative fluency;
- some canon notes are better preserved as "default for now" than as "settled uniquely," especially when later probes may reopen the same ambiguity class;
- and some archive failures look like **forced singularity**: the archive had enough public evidence to keep multiple rivals alive, but instead collapsed them into one fluent answer too early.

This suggests a missing compact surface:
**rival-set packet / branch budget / non-forced singularity**.

## External pressure from current research

Several current research lines sharpen this frame.

1. **Recent uncertainty-aware planning work treats assumptions as first-class decision variables rather than noise to be hidden.**
   Seo et al. argue that planning can improve when environmental assumptions are explicitly represented and scored before action, which pressures DelayBasin to preserve live rival assumptions instead of flattening them into one winner too early. ([`REF-0345`](../00-meta/bibliography.md))

2. **Recent workflow reliability work treats ambiguity as a branching-allocation problem, not merely a ranking problem.**
   DenoiseFlow switches between fast execution and branching exploration for ambiguous nodes, which pressures DelayBasin to preserve a small budgeted rival set when local entropy is genuinely high. ([`REF-0346`](../00-meta/bibliography.md))

3. **Recent long-horizon exploration work argues for selective dynamic branching at critical states.**
   Spark activates branching at key decision points instead of exploring everything uniformly, which pressures DelayBasin to make branch budgets explicit rather than oscillating between forced singularity and branch sprawl. ([`REF-0347`](../00-meta/bibliography.md))

4. **Recent planning-under-uncertainty work shows that single-most-likely hypotheses can fail when the true goal diverges from the modal guess.**
   Tru-POMDP builds a tree of hypotheses and hybrid belief updates because a flat best-guess strategy can break under open-ended ambiguity, which pressures DelayBasin not to treat one presently vivid branch as uniquely entitled to canon-level status. ([`REF-0348`](../00-meta/bibliography.md))

5. **Recent agentic uncertainty work treats uncertainty as something that should trigger targeted information search before bad beliefs harden into history.**
   Agentic UQ argues that epistemic uncertainty should drive retrieval expansion or reflective correction and warns that unresolved mistakes can solidify into later context, which pressures DelayBasin to keep rival sets explicit before one weakly supported branch hardens into public law. ([`REF-0349`](../00-meta/bibliography.md))

6. **Recent memory surveys say current evaluations still underweight ambiguous, non-stationary, long-horizon settings.**
   The second-half survey on foundation-agent memory argues that many benchmarks assume stationary intent and unambiguous ground truth, which pressures DelayBasin to preserve bounded rival sets in places where the archive genuinely does not yet deserve a single settled reading. ([`REF-0350`](../00-meta/bibliography.md))

## Working synthesis

A useful current synthesis is:

> DelayBasin may work better when it preserves a compact **rival-set packet / branch budget / non-forced singularity** naming the **ambiguity or decision class**, the **kept-alive rival set**, the **branch budget or survival cap**, the **next discriminating probe or settle condition**, and the **prune / merge / abstain consequence** rather than forcing one fluent winner before the archive has earned singularity.

More concretely:
- **ambiguity or decision class** — the live claim, mechanism family, continuation choice, or archive action whose honest status is still multi-hypothesis rather than singular;
- **kept-alive rival set** — the small family of explanations, branches, or interpretations that remain publicly admissible for now;
- **branch budget or survival cap** — the explicit limit on how many rivals stay live, for how long, or under what cost budget before the archive must prune, merge, or defer;
- **next discriminating probe or settle condition** — the cheapest probe, later evidence family, or decision event that would actually remove or merge a rival;
- **prune / merge / abstain consequence** — what happens when the probe lands or the budget expires: prune a branch, merge equivalent rivals, keep abstention, or escalate to a richer adjudication lane.

This is strong enough for canon as a design and mechanism candidate.
It is **not** strong enough to claim that DelayBasin has already isolated a full external particle filter, a literal hypothesis-tree controller, or a transformer-internal branching mechanism that cleanly explains the archive's behavior.

## Rival-set packets vs contradiction packets vs hold packets vs homing packets

These objects are adjacent but not identical.

- A **contradiction packet** says which consulted public surfaces disagree and what precedence or abstention rule applies.
- A **hold packet** says the honest next move is non-movement under a blocker or brake.
- A **homing packet** says which probe family can reorient the archive among ambiguity classes.
- A **rival-set packet / branch budget / non-forced singularity** says that after conflict has been named, a small set of rivals should remain explicitly alive together under budget until a discriminating probe or settle condition actually kills one.

In practice, contradiction packets say **these surfaces disagree**.
Hold packets say **do not move yet**.
Homing packets say **probe here to reorient**.
Rival-set packets say **keep these few rivals alive together, under this budget, until this probe or event earns singularity**.

## Countermodels / probes

Serious alternatives remain live:

- the archive may mostly need better contradiction packets, not a distinct rival-set object;
- some seeming rival sets may collapse into alias cleanup, timestamp repair, or better provenance ranking rather than genuine multi-hypothesis pressure;
- rival-set packets may create branch bureaucracy where a simple hold packet or homing packet would have sufficed;
- and some benefits may come from selective exploration style rather than from preserving rival sets as public law.

Useful probes include:

- compare forced-singleton summaries against small rival-set summaries under the same token budget and judge which better preserves later auditability and probe choice;
- preserve cases where two transformer-facing mechanism stories stay live and test whether naming a discriminating future probe changes the next revision decision;
- compare a rival-set packet against a pure hold packet on the same ambiguity class and see which one better preserves what should happen next;
- and preserve one case where the archive names a temporary default action without deleting rival branches, so operational choice can stay separate from ontic singularity.

## Design consequences

When several rivals remain plausibly load-bearing after contradiction handling:

- preserve a tiny rival-set packet instead of forcing one fluent winner;
- keep the rival set small and explicitly budgeted;
- tie each rival to a real discriminating probe or settle condition rather than letting branches live forever;
- allow operational defaults when needed without pretending the archive has uniquely settled the underlying question;
- and keep the packet small enough that branch discipline does not become portfolio theater.

## Transformer-facing implication

The weaker transformer-facing implication is not that DelayBasin has discovered literal particle filters inside transformers.
It is that stable long-horizon archive continuation may depend on a small **public live-hypothesis layer** over consulted and contradicted surfaces: not only what evidence is consulted and how conflicts are ranked, but **which few rival explanations are explicitly allowed to remain alive together until later probes settle them**.
That makes non-forced singularity a plausible part of the method's real leverage: the archive may improve not only by noticing conflict, but by **refusing to collapse unresolved ambiguity into one point estimate too early**.

The riskier extension is that DelayBasin may be stumbling toward an **external particle-filter or tree-of-hypotheses layer around mostly frozen transformers**, where canon, quarantine, and fresh research act like public particles or rival belief branches whose survival is governed by small probe-triggered updates rather than by one-shot narrative arbitration.
That stronger story remains quarantine-only until rival-set packets beat forced-singleton alternatives under matched budgets and probe-defined pruning events show more than ordinary cautious writing.
