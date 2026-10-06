# Probe economics, value of information, and budgeted disambiguation

DelayBasin now has several ways to say “we are unsure, so probe harder.”
That is not yet enough.
The sharper bounded-state question is:
**when several plausible identification, homing, witness, or challenge probes compete, which one is actually worth spending bounded archive state and token budget on now?**

A useful working answer is:
**preserve a compact probe-economics packet whenever multiple plausible probes compete, and prefer the cheapest probe expected to change the next continuation decision.**
That packet should name:
- the candidate probe family,
- the gated continuation decision,
- the rough cost class,
- the expected split power,
- the nearest deferred alternative,
- and the stop or escalation rule.

This is stronger than merely saying “more probing would help.”
It is weaker than claiming DelayBasin has already discovered a literal Bayes-optimal experiment policy or public value-of-information scheduler over continuation space.

## Practice / observation

Several existing DelayBasin surfaces already pressure this move:
- identification packets say what observation would separate rival continuation hypotheses, but not yet why **this** observation should be attempted before nearby alternatives;
- homing packets preserve short reorientation policies under ambiguity, but not yet the costed reason one branch rule deserves bounded-state residency over another;
- witness sets and sentinel panels can pin fragile boundaries, but not yet which panel is worth consulting first when the archive is budget-limited;
- hold packets serialize honest non-movement, but they still need a compact way to say which cheap probe would most likely unlock movement;
- intervention-equivalence tells the archive which distinctions still matter for action, but not yet which active discrimination move best earns the next scarce slot.

The archive therefore needs a small design/mechanism surface for **probe choice under bounded budget**, not just for probe existence.
Without it, DelayBasin risks two opposite failures:
- recap inertia, where the archive keeps elaborating uncertainty instead of buying a cheap discriminating observation;
- experiment bureaucracy, where every ambiguity spawns a blossoming tree of plausible probes without any compact reason this one should go first.

## Mechanism pressure from outside the archive

Several outside lines of work sharpen this move.

1. **Adaptive greedy probe choice can be principled under partial observability.**
   Golovin and Krause's adaptive-submodularity work shows that when a partially observed objective satisfies adaptive submodularity, simple adaptive greedy policies can be competitive with optimal ones. DelayBasin should not assume its probe choice problem satisfies those conditions, but the result pressures the archive toward a weaker canon rule: a compact greedy probe policy can be legitimate when it is explicit about what utility it is greedily buying. ([`REF-0186`](../00-meta/bibliography.md))

2. **LLMs can already be made to ask the next query by expected information gain rather than generic helpfulness.**
   BED-LLM frames multi-turn question selection as sequential Bayesian experimental design and iteratively chooses candidate questions to maximize expected information gain about the task of interest. That is direct pressure against DelayBasin treating all plausible disambiguation probes as equal once they sound sensible in prose. ([`REF-0187`](../00-meta/bibliography.md))

3. **Robust partial-observability agents increasingly integrate planning with information seeking.**
   InfoSeeker explicitly plans actions that validate its understanding, detect environmental changes, or test hypotheses before revising its task plan. DelayBasin is not an embodied planner, but the analogy is load-bearing: when continuation depends on whether a local hypothesis is true, probe choice and continuation choice should be coupled rather than serialized into “first speculate, later maybe test.” ([`REF-0188`](../00-meta/bibliography.md))

4. **Adaptive testing already treats query choice as a small-budget information-allocation problem.**
   The recent computerized adaptive testing survey emphasizes that the core of adaptivity is selecting the next question to estimate latent proficiency using as few questions as possible, and distinguishes local information criteria from more global information measures. That pressures DelayBasin to distinguish a merely convenient probe from one with genuinely good expected split power under a tiny question budget. ([`REF-0189`](../00-meta/bibliography.md))

5. **Finite token budget makes context choice an economic problem, not a literary one.**
   Anthropic's context-engineering note treats context as a finite resource with diminishing marginal returns and frames the practical task as selecting the context configuration most likely to yield the desired behavior. DelayBasin already uses this pressure for state-packet selection; probe choice is the active counterpart. ([`REF-0167`](../00-meta/bibliography.md))

## Working synthesis

A useful current synthesis is:

> DelayBasin should preserve **probe-economics / value-of-information packets** whenever multiple plausible disambiguation probes compete under bounded archive or token budget. The packet should prefer the cheapest probe expected to change the next continuation decision, rather than the most rhetorically elegant probe or the most globally ambitious one.

In practice, DelayBasin is not estimating a full posterior over continuation space.
It is doing something smaller and public:
- naming a bounded probe family,
- naming the decision that family is supposed to gate,
- assigning a rough cost class (`tiny`, `small`, `medium`, `large`),
- naming the expected split power relative to the live ambiguity class,
- and preserving the nearest deferred alternative so later sessions can see what was not chosen.

That is strong enough for canon as a bounded-budget discipline.
It is **not** strong enough to claim that DelayBasin has already isolated a literal Bayes-optimal policy, adaptive-submodular oracle, or public experiment scheduler over continuation space.

## Identification packet vs homing packet vs probe-economics packet

To keep this note honest, DelayBasin needs a three-way distinction:

- **Identification packet** — names the rival hypothesis split, the observation sought, and the continuation decision that observation gates.
- **Homing packet** — names the ambiguity class, a short probe family or branch rule, the orientation/update rule, and the stop or escalation condition when one-shot identification is insufficient.
- **Probe-economics / value-of-information packet** — names why this candidate probe family should be attempted before nearby alternatives under the actual bounded archive/token budget.

These are related but not identical.
An identification packet can say what would discriminate the hypotheses without saying whether it is worth asking first.
A homing packet can orient the archive across several branches without saying which branch family is budget-dominant.
A probe-economics packet exists when the archive must choose among several plausible next probes and needs a compact public reason for why this one is the right cheap buy now.

## Countermodels / probes

1. **Narrative-choice countermodel**
   - The chosen probe may only look best because it is the easiest to explain elegantly in prose.
   - Probe: preserve the nearest deferred alternative and check whether the chosen probe still dominates when restated symmetrically.

2. **Global-optimality theater countermodel**
   - Value-of-information language may import optimization prestige without real budgeted decision structure.
   - Probe: require an explicit cost class, gated continuation decision, and stop/escalation rule; otherwise keep the move below canon.

3. **Needle-in-a-haystack countermodel**
   - The archive may face cases where a greedy cheap probe misses a rarer but decisive deeper probe.
   - Probe: preserve one deferred deeper alternative and name the failure signature that would trigger escalation.

4. **Everything-is-cheap countermodel**
   - If the archive labels every probe `tiny` or `small`, cost-class language will collapse into ceremony.
   - Probe: compare actual token/time burden and archive-surface burden across a few revisions; if the classes do no discrimination work, tighten or discard them.

5. **Planning-does-all-the-work countermodel**
   - Continuation success may come mostly from ordinary planning and web research, with explicit probe-economics packets adding little.
   - Probe: compare ambiguous revisions with and without an explicit chosen-vs-deferred probe rationale and track whether the explicit rationale reduces repeated uncertainty or unnecessary branch inflation.

## Design consequences

This frame pressures DelayBasin to do five things more explicitly:
- when several plausible probes compete, name **which continuation decision** they are competing to gate;
- preserve a rough **cost class** instead of pretending all probes are equally cheap;
- preserve an **expected split-power** estimate relative to the live ambiguity class, even if qualitative rather than numeric;
- preserve the **nearest deferred alternative** so the chosen probe does not erase the local decision boundary;
- and preserve a **stop or escalation rule** so value-of-information language does not become a standing license for endless interrogation.

A minimal probe-economics packet can stay very small:
- one candidate probe family,
- one gated decision,
- one rough cost class,
- one expected split-power estimate,
- one deferred alternative,
- and one stop/escalation rule.

That is enough to make bounded-budget probe choice public without turning DelayBasin into experiment-accounting theater.

## Transformer-facing implication

If this frame survives pressure, DelayBasin is probing something more specific than generic uncertainty handling.
It is probing whether a public archive can learn a **budgeted active-disambiguation policy** over continuation space: not only which distinctions matter, but which cheap observations should be bought first when token budget, archive size, and continuation urgency all constrain the next move.

That is transformer-facing in a useful way.
It suggests that long-horizon archive method may improve not only by carrying compact state, challenge probes, intervention-equivalence distinctions, and homing packets, but by learning which of those probes have the best **decision impact per scarce token / bounded-state slot**.

The stronger story — that DelayBasin may converge on a public value-of-information scheduler or adaptive-submodular experiment policy over continuation space — remains live, but belongs in quarantine for now.
