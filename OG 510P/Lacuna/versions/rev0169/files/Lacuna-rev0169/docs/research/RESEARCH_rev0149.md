# Research notes — rev0149

## Question

What should replace a naïve “retcon the hidden world until the story looks intentional” loop?

Rev0149 investigates a narrower architecture: keep plural candidate worlds, record epistemic and causal custody explicitly, and make revision a governed transaction rather than a prose-level overwrite.

## 1. Gwern’s retcon-planning proposal

Gwern proposes repeatedly rolling out possible hidden explanations and futures, scoring them, compressing a winner into a state card, and discarding the rollout. The useful inversion is that unobserved details may remain cheap while experienced consequences become expensive.

Lacuna adopts delayed commitment but rejects two implications of a singleton state card:

- selecting one explanation can collapse useful uncertainty too early;
- a compact summary cannot distinguish observation, testimony, belief, inferred meaning, and authored causal dependency unless those categories are typed elsewhere.

Design consequence: candidate worlds remain plural and the epistemic ledger remains authoritative. Revision acts on one assignment in one world.

Source: https://gwern.net/blog/2026/llm-retcon

## 2. Assumption-based truth maintenance

Johan de Kleer’s Assumption-based Truth Maintenance System separates a problem solver from a truth-maintenance component that records environments under which propositions hold. The important architectural lesson is not to make one mutable explanation carry every context.

Lacuna’s worlds are not an ATMS implementation, but the analogy supports:

- plural contexts rather than one overwritten state;
- explicit dependency custody;
- contradiction as local incompatibility rather than global corruption;
- a kernel that validates recorded structure while an external planner searches.

Source: https://dekleer.org/Publications/Problem%20Solving%20with%20the%20ATMS.pdf

## 3. Belief revision and the politics of “minimal change”

AGM-style belief revision formalizes expansion, contraction, and revision under consistency and minimal-change principles. It also reveals that “minimal” is never neutral: a revision operator needs an ordering or policy over what should be preserved.

Lacuna therefore does not advertise a mathematically privileged retcon. Rev0149 exposes a named burden policy and blockers. The score is inspectable and replaceable; hard commitments and binding consequences are explicit author policy.

Source: https://plato.stanford.edu/entries/logic-belief-revision/

## 4. Possible-world character belief

Shirvani, Ware, and Farrell model character beliefs using epistemically possible worlds in narrative planning. Their work reinforces that global planner alternatives and an individual character’s alternatives are different structures.

Lacuna currently stores perspective-scoped assertions rather than a full recursive belief graph. Candidate worlds remain planner hypotheses; they must not be mistaken for everything a character considers possible. A later agent-relative possibility layer should preserve that separation.

Source: https://ojs.aaai.org/index.php/AIIDE/article/view/12928

## 5. LLMs as planning guides, not sovereign state stores

Recent hybrid narrative-planning work explores using language models to guide search while retaining symbolic state and planner validation. This division is compatible with Lacuna’s intended host pattern:

```text
LLM proposes meaning, narration, and candidate deltas
kernel validates identity, custody, compatibility, and access
planner/search layer explores alternatives outside the ledger
```

The model can be an excellent abductive proposal generator without becoming the database, verifier, or final authority.

Sources:

- https://cs.uky.edu/~sgware/reading/papers/farrell2024large.pdf
- https://dl.acm.org/doi/10.1145/3723498.3723815
- https://arxiv.org/html/2505.03547v1

## 6. Orchestrated Reality and Plan-Diff-Validate-Apply

*Orchestrated Reality* (Huang, Li, and Fang, 2026) treats persistent game state as canonical JSON and uses a Plan-Diff-Validate-Apply pipeline with schema-validated, content-hashed deltas. This independently supports several Lacuna choices:

- prose should be a projection, not the state store;
- transitions should be proposed as structured deltas;
- validation precedes application;
- committed deltas should be content-bound.

The central difference is deliberate. Orchestrated Reality describes one singleton canonical state owned by an orchestration agent. Lacuna stores a typed ledger plus several latent candidate worlds because an adaptive mystery may need multiple explanations to remain live. “Canonical state” in Lacuna is the custody history and anchored observation surface, not one fully decided hidden world.

Source: https://arxiv.org/abs/2606.16014

## 7. PDDL-Mind and explicit state evolution

*PDDL-Mind* (Zhu et al., 2026) argues that many apparent belief-reasoning failures arise from unreliable implicit state tracking. It decouples explicit, verified state evolution from belief inference.

This is directly relevant to the Lacuna boundary:

- physical and custody transitions should be explicit and replayable;
- belief and interpretation should be represented separately;
- a language model should not silently update both by narrating a sentence.

Source: https://arxiv.org/abs/2604.17819

## 8. Dynamic epistemic and narrative systems

Recent work on epistemic reasoning and uncertainty in narrative planning continues to show that belief states, temporally possible worlds, and authorial uncertainty are first-class computational objects rather than incidental prose annotations.

The practical caution is complexity: recursive belief, logical closure, and uncertain state spaces grow quickly. Lacuna should add such machinery only as disposable, inspectable projections above original custody.

Sources:

- https://ojs.aaai.org/index.php/AIIDE/article/view/36848
- https://ojs.aaai.org/index.php/AIIDE/article/download/36817/38955/40894
- https://arxiv.org/html/2602.16162v1

## Synthesis

The better-than-retcon architecture is not “never revise.” It is:

1. preserve immutable observations and transition custody;
2. keep several hidden-world hypotheses alive;
3. type facts, beliefs, reports, constraints, and meaning separately;
4. distinguish ambient exposure from authored dependence;
5. bind revision authorization to a current, inspectable state;
6. retain downstream repair debt rather than silently rewriting it;
7. let an LLM search and narrate outside the kernel;
8. validate typed deltas before presenting them as committed world change.

## What rev0149 implements

- no-clobber world assignment slots;
- digest-bound governed revision with lineage;
- monotone commitment transitions;
- explicit consequence links and bounded traversal;
- transparent revision burden;
- repair debt for ended endpoints;
- perspective explanation noninterference;
- database schema 4 and migration from schemas 1–3.

## Research still needed

- controlled studies separating causal agency from retrospective significance;
- policies for moving or discharging consequences across revisions;
- counterfactual probes against the same world population;
- character identity and motive conservation metrics;
- particle diversity and anti-conspiracy priors;
- cryptographic commitment receipts for fair-play mysteries;
- semantic checks between generated prose and declared disclosure operations.
