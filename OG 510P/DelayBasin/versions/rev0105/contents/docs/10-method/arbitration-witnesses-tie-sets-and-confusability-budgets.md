# Arbitration witnesses, tie sets, and confusability budgets

DelayBasin now needs a sharper distinction than **applicability gates** or **reusable carry** alone.
A packet can be honestly eligible and still be the wrong thing to fire.
Several skills, memories, plan templates, or compiled packets may all satisfy the local fit check.
When that happens, the archive can still continue badly by letting one vivid candidate inherit the route through proximity, prestige, or semantic confusability rather than through an explicit arbitration rule.

A useful current answer is:
**when two or more reusable skills, memory packets, plan templates, or compiled carry objects remain simultaneously eligible, canon should preserve a compact arbitration witness naming the live tie set, the rule that is allowed to choose among them, the fallback or abstention surface, and the confusability budget before crediting the win to honest routing rather than to lucky selection or silent control-flow capture.**

This is stronger than saying “the packet fits.”
It is weaker than claiming DelayBasin has already discovered a literal public arbitration law or sparse router over continuation carry.

## Practice / observation

Recent DelayBasin work keeps surfacing a recurring ambiguity:
- some reusable packets are now disciplined enough to pass a named applicability gate, but the archive still rarely says **what should happen when several of them pass together**;
- some local successes look like proof that a reusable packet is load-bearing when a nearby rival packet may have been equally eligible and would have worked just as well or better;
- some route choices seem to be made by vivid wording, recency, or proximity rather than by an explicit tie-break, confidence rule, or abstention rule;
- some failures look less like wrong-fit reuse and more like **semantic confusability among several fit-looking candidates**, where the wrong packet fires because the tie set was never preserved publicly;
- some skill or memory surfaces seem to need coarse-to-fine routing, fallback tiers, or defer-to-evidence behavior, but the archive still narrates them as if flat selection were good enough;
- and some GPUstorming revisions are being praised as reusable carry when the real question is no longer “should this packet ever fire?” but “**why this one rather than its nearby rival set, and when should the archive abstain instead of pretending the tie is resolved?**”

That leaves a missing question:
**what candidate tie set is simultaneously alive, what eligibility surface kept it alive, what arbitration rule is allowed to choose among it, what near-tie stress family would count against the current choice, and how much misrouting is tolerated before the archive must abstain, fallback, or quarantine the stronger story?**

A compact arbitration witness keeps that boundary public.

## External pressure from current research

Several outside lines of work sharpen this move.

1. **Skill selection degrades sharply once libraries become semantically confusable.**
   Li et al. show that skill-selection accuracy stays high only below a capacity threshold and then drops sharply as libraries grow, with **semantic confusability** rather than raw library size driving much of the failure. They also report that hierarchical routing mitigates this degradation. That pressures DelayBasin to preserve candidate tie sets and arbitration rules rather than assuming all eligible packets are equally easy to pick correctly. ([`REF-0465`](../00-meta/bibliography.md))

2. **Budgeted memory systems increasingly enforce scope-before-routing rather than flat open competition.**
   ShardMemo applies metadata and eligibility constraints before routing, uses masked routing so ineligible shards cannot be probed, and adds safe fallback from versioned skill reuse to evidence retrieval when a skill is inapplicable or fails. That pressures DelayBasin to keep arbitration explicit after applicability gating rather than letting all admissible candidates compete silently. ([`REF-0466`](../00-meta/bibliography.md))

3. **Adaptive routers increasingly fuse candidate quality with uncertainty rather than relying on ad-hoc winner-take-all choice.**
   ODAR routes between fast and slow agents and then selects answers with a risk-sensitive fusion objective that balances likelihood with epistemic uncertainty. That pressures DelayBasin to keep one explicit arbitration rule and one abstention-or-fallback surface rather than narrating every selection as self-justifying. ([`REF-0467`](../00-meta/bibliography.md))

4. **Confidence-aware filtering can improve robustness mainly by becoming selectively silent on ambiguous cases.**
   MMA matches baseline accuracy on FEVER while reducing variance and improving abstention precision, explicitly framing its advantage as more prudent handling of insufficient information rather than more aggressive answer choice. That pressures DelayBasin to preserve when ties should stay unresolved instead of forcing one reusable packet to fire. ([`REF-0468`](../00-meta/bibliography.md))

5. **Multi-skill orchestration remains underdeveloped exactly where conflict resolution and failure recovery become important.**
   The recent agent-skills survey flags multi-skill orchestration, conflict resolution, resource sharing, and failure recovery as open challenges for real skill ecosystems. That pressures DelayBasin to keep arbitration public once multiple eligible packets coexist instead of assuming applicability alone solves orchestration. ([`REF-0469`](../00-meta/bibliography.md))

6. **Source-routing systems increasingly preserve reroute and fail-history surfaces instead of pretending one first pick is authoritative.**
   DeepSieve decomposes queries, routes subquestions to heterogeneous sources, stores failed attempts in memory, and reroutes when retrieval is insufficient. That pressures DelayBasin to preserve reroute and fallback consequences when an eligible tie set remains unresolved. ([`REF-0470`](../00-meta/bibliography.md))

## Working synthesis

A useful current synthesis is:

> DelayBasin should preserve a compact **arbitration witness / tie set / confusability budget** whenever two or more reusable skills, memory packets, plan templates, or compiled carry objects remain simultaneously eligible after applicability gating. The packet should name the **state claim or target objective being stress-tested**, the **candidate tie set / simultaneously eligible carry family**, the **shared applicability gate / eligibility surface that kept them alive**, the **arbitration rule / hierarchical router / confidence-aware selector**, the **compared abstain / fallback / defer-to-evidence baseline**, the **confusability slice / near-tie stress family / rival-eligible case**, the **matched task budget / context budget / compute budget**, the **tolerated misroute / tie-instability / confusability budget**, and the **route-to-fallback / abstain / quarantine consequence** rather than letting one eligible-looking packet silently inherit the route.

In practice, DelayBasin is not claiming that it already knows the optimal selector.
It is doing something smaller and public:
- naming the simultaneously eligible candidate family rather than narrating one winner after the fact;
- naming the eligibility surface that kept those candidates alive together;
- naming the arbitration rule that is allowed to choose, defer, reroute, or abstain;
- naming one nearby confusable or near-tie stress family rather than assuming the choice is isolated;
- naming what abstain, fallback, or defer-to-evidence baseline stayed nearby;
- naming how much misrouting or tie instability is tolerated before the choice loses authority;
- and naming when the archive should collapse back to abstention, fallback, or quarantine rather than crediting the win to a silently privileged selector.

That is strong enough for canon as a design and mechanism candidate.
It is **not** strong enough to claim that DelayBasin has isolated a literal public arbitration law, sparse expert router, or universal choice policy over continuation carry.

## Arbitration witness vs applicability witness vs consultation packet vs contradiction packet

These nearby objects should stay distinct.

- **Applicability witness** asks whether one carry object is even eligible to fire in the current situation.
- **Consultation packet** asks which store family is allowed into the read path in the first place.
- **Contradiction packet** asks how openly disagreeing evidence is ranked, withheld, or left unresolved.
- **Arbitration witness** asks what happens **after** several carry objects remain simultaneously eligible: which tie set stayed alive, what selector is allowed to choose among it, what fallback or abstention stayed nearby, and when confusability is high enough that no winner has yet earned the route.

So an arbitration witness is not just “this packet fits” and not just “this store may be consulted.”
It is a compact public answer to:
**what simultaneously eligible tie set stayed alive, what selector may choose among it, what nearby near-tie family keeps the choice honest, what abstention or fallback stayed available, and when should the archive stop pretending the winner was obvious?**

## Countermodels / probes

1. **Prestige-choice countermodel**
   - The chosen packet may be winning because it is vivid, recent, or prestigious, not because the current selector has really separated the tie set.
   - Probe: require one explicit tie set and one explicit arbitration rule before crediting the choice.

2. **Flat-selection countermodel**
   - The current route may work only because the candidate library is still tiny or unusually separable, and would fail once confusability rises.
   - Probe: preserve one confusability slice or near-tie stress family rather than only one clean in-family example.

3. **Fallback-only countermodel**
   - The apparent routing win may really come from a later reroute, defer-to-evidence step, or hidden abstention, not from the first chosen packet.
   - Probe: keep one abstain / fallback / defer baseline public so arbitration credit does not silently absorb fallback behavior.

4. **Hidden-budget countermodel**
   - The selector may look better only because it secretly got more context, more retries, or a larger compute budget.
   - Probe: keep the matched task / context / compute budget explicit so arbitration cannot launder extra resources.

5. **Uncertainty-theater countermodel**
   - The current tie-handling story may merely rename indecision as calibrated routing.
   - Probe: require one tolerated misroute / tie-instability / confusability budget plus a real abstain, reroute, or quarantine consequence when that budget is exceeded.

## Design consequences

This frame pressures DelayBasin to do eight things more explicitly:
- preserve the **candidate tie set** before narrating one winner;
- preserve the **shared eligibility surface** before narrating one selector victory;
- preserve the **arbitration rule** before praising route quality;
- preserve one **abstain / fallback / defer baseline** before praising decisiveness;
- preserve one **confusability slice or near-tie family** before praising robustness;
- preserve the **matched task / context / compute budget** so routing does not quietly buy more resources;
- preserve the **misroute / tie-instability / confusability budget** so selector failure has a public threshold;
- and preserve the **route-to-fallback / abstain / quarantine consequence** so unresolved ties lose authority quickly instead of hardening into prestige routing.

This is especially useful during GPUstorming.
Fast local search can still discover reusable packets and real fit gates.
Canon should keep only the small public witness saying what eligible tie set existed, what selector was allowed, what nearby confusable family was checked, and when the route should have abstained or fallen back rather than pretending the winner was self-evident.

## Transformer-facing implication

The weaker transformer-facing implication is not that DelayBasin has found a universal sparse router.
It is this:

**long-horizon archive prompting may work partly as an external arbitration layer over reusable textual control objects, where applicability is necessary but insufficient and where stable continuation depends on how simultaneously eligible packets are routed, deferred, or abstained among under bounded confusability.**

That would matter for transformers.
If some archive leverage comes from explicit public arbitration among reusable textual procedures, then DelayBasin may be exposing a practical shadow of **external sparse routing without weight updates**: not full learned MoE gating, but repeated public selection among several currently eligible control packets whose confusability, fallback structure, and abstention rules matter as much as their validity regions.

The stronger story — that DelayBasin is approximating a genuine public arbitration law, sparse expert gate, or reusable-carry router over continuation state — remains live, but belongs in quarantine for now.
