# Research notes — rev0148

Research was reviewed on 2026-06-22. These sources guide design; citation does not imply that Lacuna implements each system.

## 1. Horswill’s Retcon already treats cardinality as story-world theory

Ian Horswill’s Retcon separates changing **story state** from ordinary in-world state and represents acceptable story worlds as models of authored constraints. Its implemented logic includes `Unique`, `AtMost`, `AtLeast`, and `Exactly` forms in the story-world theory. Fragment assumptions themselves are more restricted and cannot be cardinality constraints or implications.

Source:
- Ian Horswill, *Retcon: A Least-Commitment Story-World System*: https://www.exag.org/papers/Retcon%20A%20Least-Commitment%20Story-World%20System.pdf

Lacuna consequence:
- set-level bounds belong in the integrity ontology, not as prose hints;
- constraint custody and story fact custody remain distinct;
- least commitment needs a way to reject impossible completions without prematurely selecting one completion.

## 2. Open-world story planning makes “undetermined” a design resource

Riedl and Young’s open-world planning work addresses story worlds whose initial states are not fully specified. The central architectural lesson is that a planner can commit assumptions as needed instead of requiring a total world description before planning begins.

Source:
- Mark O. Riedl and R. Michael Young, *Open-World Planning for Story Generation*: https://www.ijcai.org/Proceedings/05/Papers/post-0020.pdf

Lacuna consequence:
- a missing member cannot count as false;
- an exactly-one constraint can remain satisfiable while every member is unresolved;
- lower-bound failure occurs only when explicit falsehoods eliminate all possible completions.

## 3. Cardinality deserves a first-class representation

Boolean cardinality constraints are a standard class of constraints with specialized encodings rather than merely informal collections of pairwise rules. Sinz’s work analyzes compact CNF encodings for such constraints, underscoring that set-level bounds are their own representational object.

Source:
- Carsten Sinz, *Towards an Optimal CNF Encoding of Boolean Cardinality Constraints*: https://www.carstensinz.de/papers/CP-2005.pdf

Lacuna consequence:
- preserve the authored group and its bounds directly;
- do not explode an at-most-K rule into opaque pairwise records;
- postpone solver compilation until Lacuna needs formulas beyond direct bounds.

## 4. Plot adaptation must be bounded

Wu et al.’s Plot-based Reflection periodically adjusts plot chains based on player behavior. The authors explicitly restrict one reflection step to altering no more than one incomplete plot or inserting one plot because models otherwise tend to over-adjust and introduce incoherent or unrelated material.

Source:
- Hongqiu Wu et al., *Towards Enhanced Immersion and Agency for LLM-based Interactive Drama*: https://aclanthology.org/2025.acl-long.546/

Lacuna consequence:
- future retcon/planning adapters need immutable grants and revision budgets;
- adaptation must operate against explicit constraints rather than rewriting an unconstrained canon paragraph;
- one bounded semantic delta per accepted turn is safer than opaque global replanning.

## 5. Reincorporation does not automatically become felt agency

Marlinspike’s evaluation found that reincorporation produced more unified structures and included more significant player actions, yet players did not report corresponding gains in story quality or story-level agency.

Source:
- Zach Tomaszewski, *On the Use of Reincorporation in Interactive Drama*: https://ojs.aaai.org/index.php/AIIDE/article/view/12468

Lacuna consequence:
- cardinality and relation constraints protect coherence but do not prove the player caused the outcome;
- future evaluation must compare counterfactual trajectories, not just callback density;
- some details should remain incidental rather than becoming compulsory clues.

## 6. Declarative narrative planning remains relevant—but belongs above custody

Recent answer-set narrative planning research continues to use declarative constraints to generate plans with authored goals and character considerations. That supports a future solver-backed planner, but it does not erase the need to separate generated conclusions from original assertions and observations.

Source:
- Cory Siler and Stephen G. Ware, *An Answer Set Encoding for Narrative Planning with Character Intentions and Conflict*: https://ojs.aaai.org/index.php/AIIDE/article/download/36817/38955/40894

Lacuna consequence:
- a future ASP/SAT adapter should consume a read-only snapshot and return a typed proposal;
- solver consequences must cite rules and premises and remain labelled as derived;
- the event ledger should continue to own accepted custody, not the planner’s transient search state.

## 7. Gwern’s useful inversion still needs an epistemic ledger

Gwern’s retcon-planning loop makes experienced history expensive and unseen explanation cheap. The danger is compressing one currently convenient hidden explanation into a new canon paragraph and repeatedly rationalizing from it.

Source:
- Gwern Branwen, *LLM Retcon*: https://gwern.net/blog/2026/llm-retcon

Lacuna consequence:
- maintain several partial worlds;
- represent observed facts, reports, beliefs, constraints, and unresolved members separately;
- use constraints to prune impossibility without equating the surviving completion with observed truth;
- keep audience and planner knowledge structurally separate.

## Synthesis for rev0148

The research supports six implementation rules:

1. **Groups are first-class.** The authored rule must survive as a group, not disappear into pairwise debris.
2. **Undetermined is live state.** Unknown members remain possible completions.
3. **Constraint is not closure.** Rejection may be automatic; materialized truth may not be.
4. **Adaptation is budgeted.** Future model/planner changes must be typed and bounded.
5. **Diagnostics are disclosures.** A hidden rule can leak through its explanation even when the rule itself is omitted.
6. **Coherence is not agency.** Integrity constraints are prerequisites, not evidence of meaningful player causation.

## Questions left open

- Should a future derived-fact layer expose forced cardinality consequences without storing them as authored assignments?
- How should mystery hosts commit to hidden constraints cryptographically while withholding their content?
- What revision-cost policy should govern adding or retiring high-impact constraints after disclosures?
- When should large groups compile to SAT/ASP, and how should solver explanations map back to custody records?
- How should character knowledge represent uncertainty over group members without copying the planner’s global constraint ontology?
