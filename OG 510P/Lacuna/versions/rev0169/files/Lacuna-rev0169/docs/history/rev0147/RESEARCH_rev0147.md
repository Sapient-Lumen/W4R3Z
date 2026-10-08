# Research notes — rev0147

Research was reviewed on 2026-06-22. These notes inform architecture; they are not claims that Lacuna implements every cited system.

## 1. Truth-maintenance systems: reasons should be explicit

Jon Doyle’s truth-maintenance work treats beliefs as records supported by justifications and updates dependent beliefs when supporting assumptions change. The important lesson for Lacuna is not to copy a classical TMS wholesale. It is that **reasons and dependency structure must be queryable objects**, not model recollection.

Source:
- Jon Doyle, *A Truth Maintenance System*, MIT AI Laboratory, 1978: https://dspace.mit.edu/handle/1721.1/5733

Design consequence:
- add `explain` as a custody/dependency query;
- keep the query honest about what it does not prove;
- later compute revision cost from explicit dependents rather than from narrative intuition alone.

## 2. Assumption-based TMS: preserve several environments

Johan de Kleer’s ATMS represents conclusions across multiple consistent assumption environments instead of forcing one total belief state. That is unusually close to Lacuna’s central objection to a single retconned “winning world.”

Source:
- Johan de Kleer, *An Assumption-based TMS*: https://dekleer.org/Publications/An%20Assumption-based%20TMS.pdf
- Johan de Kleer, *Problem Solving with the ATMS*: https://dekleer.org/Publications/Problem%20Solving%20with%20the%20ATMS.pdf

Design consequence:
- retain a population of candidate worlds;
- treat world compatibility as an environment test;
- do not collapse a relation into automatic global truth;
- reserve future work for compact world deltas, nogoods/cardinality, and diversity-preserving resampling.

## 3. Provenance models: provenance is structured but not truth

W3C PROV distinguishes entities, activities, agents, derivations, attribution, generation, use, and invalidation. Lacuna’s domain is narrower, but the separation reinforces a crucial rule: recording where a statement came from is not the same as certifying the statement.

Source:
- W3C, *PROV-DM: The PROV Data Model*: https://www.w3.org/TR/prov-dm/

Design consequence:
- explanations expose origin and termination events plus typed structural links;
- source, actor, claim, and assertion remain separate namespaces;
- every response carries a nonclaim against reading provenance as proof.

## 4. Reincorporation: relevance is not causality

Marlinspike selects later scenes that reincorporate earlier events and player actions. Its evaluation is a useful warning for “better retconning”: more structurally unified stories can include more player material without necessarily increasing perceived story quality or agency.

Source:
- Zach Tomaszewski, *Marlinspike: An Interactive Drama System*: https://ojs.aaai.org/index.php/AIIDE/article/view/12468

Design consequence:
- do not make every incidental detail a hidden clue;
- score causal divergence separately from retrospective thematic relevance;
- preserve dead matter and coincidence penalties in future particle scoring;
- use claim relations for world integrity, not for gratuitous callback density.

## 5. Open-world planning: delay commitment deliberately

Work on open-world story planning leaves parts of the initial state undecided and commits them only as planning requires. This supports Gwern’s useful inversion while also suggesting that late binding needs explicit consistency machinery.

Source:
- Mark Riedl and R. Michael Young, *Open-World Planning for Story Generation*: https://cdn-dev.vanderbilt.edu/t2-my-dev/wp-content/uploads/sites/3191/2021/03/InteractiveNarrative.pdf

Design consequence:
- unobserved state remains plural;
- explicit relations prune impossible alternatives;
- observed consequences and anchors constrain every surviving alternative;
- late commitment is a controlled operation, not permission for unconstrained rewriting.

## 6. Gwern’s retcon-planning proposal: keep the inversion, reject premature collapse

Gwern proposes repeatedly inferring a hidden explanation for the story-so-far, rolling it forward, compressing the result, and discarding the rollout. The strongest insight is to make the experienced past expensive and the unseen future cheap.

Source:
- Gwern Branwen, *LLM Retcon*: https://gwern.net/blog/2026/llm-retcon

Lacuna’s divergence:
- store typed epistemic custody instead of a canon paragraph;
- maintain several latent worlds instead of one compressed winner;
- distinguish constraints from inferred facts;
- audit origin and dependence;
- preserve perspective boundaries;
- eventually measure causal agency and counterfactual depth, not only coherence.

## Synthesis for rev0147

The implementation follows five derived rules:

1. **Compatibility is explicit.** Distinct claims need first-class relations.
2. **Unknown remains open.** Constraints reject known bad pairs; they do not close missing values.
3. **Reasons are inspectable.** Every relation has source/rationale/custody; every record can expose direct lineage.
4. **Plurality survives.** A relation prunes impossible worlds but does not select one winner.
5. **Provenance is not proof.** Explanations describe recorded structure and visibility, never certify truth or quality.

## Research questions left open

- Should future logical closure be computed per world, per agent, or both?
- How should exactly-one and at-least-one groups interact with unknown values?
- Can revision cost be derived from visible disclosures and causal dependents without rewarding overconnected plots?
- What is the minimal counterfactual test that distinguishes causal agency from retrospective relevance?
- How should a system cryptographically commit to mystery constraints without leaking them to the player?
