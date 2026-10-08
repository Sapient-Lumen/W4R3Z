# Research notes — rev0152

## Question

How should Lacuna move from merely retaining several hidden-world hypotheses to updating planning attention after evidence—without turning authored scores into truth, collapsing the population, double-counting evidence, or leaking hidden ontology into the audience view?

Rev0152 implements the smallest governable answer: **complete-population likelihood reweighting with immutable factor custody**. It deliberately does not implement proposal, resampling, pruning, or winning-world selection.

## Synthesis

### Delayed commitment is a latent-state problem, not a prose-editing problem

Gwern’s “LLM retcon” proposal is strongest when read as late binding: preserve player-visible events, defer unseen causes, roll out possible explanations, and commit only as consequences force commitment. The weak implementation is repeated replacement of one hidden outline. The stronger implementation maintains a population of explicit partial worlds and treats narration as a projection rather than the state itself.

Ian Horswill’s *Retcon* system supplies an important precursor: story fragments carry assumptions, and a constraint solver preserves compatible story-world choices. Riedl and Young’s open-world planning work likewise separates facts that must be fixed for planning from facts that can remain undecided. These precedents support Lacuna’s open-world ledger, but they do not by themselves solve evidence custody, model-relative weights, or audience-safe access.

Sources:

- [Gwern, “LLM Retcon”](https://gwern.net/blog/2026/llm-retcon)
- [Horswill, “Retcon: A Least-Commitment Story-World System”](https://www.exag.org/papers/Retcon%20A%20Least-Commitment%20Story-World%20System.pdf)
- [Riedl and Bulitko, “Interactive Narrative: An Intelligent Systems Approach”](https://cdn-dev.vanderbilt.edu/t2-my-dev/wp-content/uploads/sites/3191/2021/03/InteractiveNarrative.pdf)

### Reincorporation can increase structural unity without increasing experienced agency

Marlinspike’s reincorporation work is a direct warning against optimizing callbacks as a proxy for player agency. A system can make more player actions appear structurally relevant without producing a corresponding subjective improvement. Plot-based Reflection offers a newer LLM analogue: periodically revising the plot can improve measured agency, while over-adjustment and invented state remain practical failure modes.

Lacuna therefore keeps **retrospective significance**, **authored consequence custody**, and **causal effect** separate. Particle weights are planning attention. They are not proof that a player action caused a future or that the resulting story is better.

Sources:

- [Tomaszewski, “On the Use of Reincorporation in Interactive Drama”](https://cdn.aaai.org/ojs/12468/12468-52-15996-1-2-20201228.pdf)
- [Wu et al., “Towards Enhanced Immersion and Agency for LLM-based Interactive Drama”](https://arxiv.org/abs/2502.17878)

### Model uncertainty argues for averaging, but Lacuna has authored models rather than calibrated statistical models

Bayesian model averaging formalizes a useful principle: predictions should account for uncertainty across models rather than silently conditioning on one selected model. That principle maps cleanly to plural hidden worlds. Its numerical guarantees do not transfer automatically. Lacuna’s candidate worlds are authored, incomplete, dependent, and rarely generated from a known probabilistic model family.

Consequently rev0152 uses the familiar update shape

```text
posterior attention(world) ∝ prior attention(world) × authored likelihood(evidence | world)
```

but labels every quantity honestly. The result is a normalized planning distribution, not a certified posterior probability.

Source:

- [Hoeting, Madigan, Raftery, and Volinsky, “Bayesian Model Averaging: A Tutorial”](https://projecteuclid.org/journals/statistical-science/volume-14/issue-4/Bayesian-model-averaging--a-tutorial-with-comments-by-M/10.1214/ss/1009212519.full)

### Sequential Monte Carlo says reweighting and resampling are different operations

Sequential Monte Carlo normally alternates several distinct acts: propose or propagate particles, calculate incremental weights, normalize, diagnose degeneracy, resample when policy calls for it, and often rejuvenate with a transition kernel. Combining those acts into one opaque “update worlds” command would erase exactly the custody Lacuna is meant to preserve.

Rev0152 therefore implements only the weighting step. It records the complete prior population, one likelihood for every live or selected world, the normalized result, and concentration diagnostics. World creation, status changes, selection, pruning, merging, and future resampling remain separate operations.

The literature also emphasizes particle impoverishment and mode loss. Persistent sampling retains particles across iterations to improve diversity; related work uses partial or diversity-aware resampling. The design lesson for Lacuna is not to copy a statistical algorithm mechanically. It is to make ancestry, elimination, minority preservation, and proposal policy explicit before any resampler exists.

Sources:

- [Naesseth, Lindsten, and Schön, “Elements of Sequential Monte Carlo”](https://arxiv.org/abs/1903.04797)
- [Karamanis and Seljak, “Persistent Sampling: Unleashing the Potential of Sequential Monte Carlo”](https://arxiv.org/abs/2407.20722)
- [Saeedi et al., “Variational Particle Approximations”](https://jmlr.org/papers/v18/15-615.html)

### ESS and entropy are concentration diagnostics, not quality scores

The common effective-sample-size proxy, `1 / Σw²`, is useful for describing weight concentration. It is not a direct count of independent good explanations, and later work has stressed the assumptions behind treating it as a literal effective sample size. A 2026 analysis further connects families of ESS approximations to entropy measures.

Lacuna therefore reports ESS, Shannon entropy, normalized entropy, and maximum mass together. It never uses ESS to auto-prune, resample, canonize, or claim narrative diversity. Two worlds can carry distinct IDs while encoding the same explicit valuation; rev0152 reports those duplicate-valuation groups separately.

Sources:

- [Martino, Elvira, and Louzada, “Effective Sample Size for Importance Sampling Based on Discrepancy Measures”](https://arxiv.org/abs/1602.03572)
- [Elvira, Martino, and Robert, “Rethinking the Effective Sample Size”](https://arxiv.org/abs/1809.04129)
- [Martino and Elvira, “Effective Sample Size Approximations as Entropy Measures”](https://arxiv.org/abs/2602.22954)

## Deductions implemented in rev0152

### 1. Update the complete eligible population

A likelihood vector must cover every live or selected candidate world exactly once. Normalizing over a hidden subset would create a false denominator and make the resulting weights incomparable with the bank the host believes it updated.

### 2. Bind a review to a deterministic bank digest

The bank digest covers each eligible world’s ID, status, raw weight, explicit valuation fingerprint, and broader custody fingerprint. Any change to membership, status, weight, assignments, commitment, or assignment provenance stales the review.

### 3. Treat one assertion as one multiplicative factor

Applying the same evidence assertion twice is accidental exponentiation. Rev0152 refuses a second review or update for an already-applied assertion and enforces the rule with both runtime validation and a unique database index. A same-change duplicate rolls back atomically.

### 4. Preserve factor history after supersession

If evidence is later superseded, Lacuna does not silently reverse the old multiplication. The update remains immutable and the bank exposes **reweighting debt**. This is intentionally uncomfortable: a normalized vector can still be epistemically stale.

A future factor-ledger recomputation protocol should reconstruct weights from declared base weights and the still-authorized factor set. Until then, the system records the debt rather than fabricating a repaired posterior.

### 5. Fingerprint valuation separately from custody

Two worlds may have the same explicit truth assignments but different IDs, sources, commitment histories, or unresolved latent detail. Rev0152 computes:

- a valuation fingerprint over explicit ontic assignments; and
- a custody fingerprint over assignment identity, commitment, confidence, lineage, and provenance references.

Different likelihoods for valuation-equivalent worlds are surfaced as a diagnostic seam. The system does not assume they are wrong, because the assessor may be using distinctions not represented by the current valuation fingerprint.

### 6. Keep the bank planner-only

The global bank, update history, rationales, evidence-factor list, and concentration diagnostics can reveal the existence and topology of hidden explanations. They are present only in unscoped planner context. Audience context and world-scoped director context omit them structurally.

### 7. Repair schema lineage rather than pretending two schema 6s were one

The canonical fair-play rev0151 and an experimental particle sibling independently used database schema number 6. Rev0152 keeps the delivered fair-play branch as its parent, advances the combined physical schema to 7, and refuses nonempty event-unowned particle rows during migration. This is a provenance decision, not merely a table-shape decision.

## Negative results and unresolved risks

- A likelihood of zero leaves a world record present but gives it zero future mass. This is effective extinction without an explicit prune event and deserves a future strict policy.
- Authored likelihoods may be uncalibrated, mutually dependent, strategically biased, or based on facts absent from the world fingerprint.
- Superseded factors create visible debt but are not yet retractable or recomputable.
- Ordinary floating-point multiplication will eventually underflow in long campaigns; a factor ledger and log-weight replay are preferable.
- The bank contains only worlds already proposed. It cannot discover a missing explanation.
- ESS can look healthy while all worlds share one blind spot, or look low while a single explanation is genuinely dominant.
- Reweighting does not measure causal agency, counterfactual robustness, character integrity, thematic merit, or player enjoyment.

## Next experiments

1. **Factor-ledger replay:** separate authored base weight from every evidence factor; recompute current weight after supersession or policy changes.
2. **Zero-likelihood governance:** require an explicit extinction review, epsilon floor, or reversible quarantine rather than permitting silent zero-mass persistence by default.
3. **Proposal and ancestry:** add new candidate worlds from explicit parent deltas with proposal custody before any resampling exists.
4. **Diversity diagnostics:** compare ID count, valuation groups, claim-disagreement coverage, and semantic clusters rather than trusting ESS alone.
5. **Counterfactual seam tests:** vary one player action while keeping initial custody fixed; measure causal outcome divergence separately from retrospective reinterpretation.
6. **Likelihood calibration exercises:** give independent assessors the same evidence packet and quantify disagreement, hidden-feature reliance, and confidence inflation.
7. **Narrative benchmark adapter:** log full model-in-the-loop trajectories and evaluate leakage, contradiction, identity drift, false reincorporation, and human-perceived agency.

## Rev0152 research conclusion

A better-than-retcon engine should not repeatedly choose a new secret past. It should maintain plural partial worlds, expose exactly why their planning weights changed, preserve every evidence factor in custody, and refuse to confuse concentration with truth. **The epistemic ledger remains primary; the particle bank is one revisable planner projection over it.**
