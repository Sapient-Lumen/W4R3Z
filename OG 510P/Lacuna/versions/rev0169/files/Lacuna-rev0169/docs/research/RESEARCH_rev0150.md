# Research notes — rev0150

## Question

Once a system refuses silent retconning and makes downstream consequence debt visible, what is the correct way to repair that debt?

Rev0150 investigates a narrow answer: **forward replacement with immutable predecessor/successor custody**, authorized by a state-bound review. It rejects both destructive rollback and automatic inheritance.

## 1. Revision should be represented as derivation, not overwrite

The W3C PROV data model defines revision as a subtype of derivation: the resulting entity is a revised version of an original. PROV also notes that binary relations can be expanded into identified, n-ary relations carrying application details.

Lacuna applies that structure to consequence custody:

- predecessor and successor remain separate entities;
- the replacement relation has its own identity;
- reason, review digest, and sequence are properties of that relation;
- chains remain inspectable rather than compressed into the newest row.

This is stronger than storing `previous_id` on the successor alone because the repair act itself can be explained, verified, and later extended.

Source: W3C, *PROV-DM: The PROV Data Model*, https://www.w3.org/TR/prov-dm/

## 2. Correction is not necessarily time travel

Martin Fowler’s Retroactive Event pattern distinguishes current incorrect reality, a counterfactual correct branch, and the corrected live reality. It also warns that fully replaying history becomes difficult when downstream effects or external systems already exist.

Adaptive fiction has the same problem. A player may have heard dialogue, made a decision, or caused an external game-engine effect based on the old dependency. Replaying an alternate past does not automatically repair those experienced consequences.

Lacuna therefore does not insert an event into the historical sequence or rewrite prior events. It appends a present-tense correction:

```text
we previously held consequence C0;
we now end it and author successor C1;
R records why this replacement happened.
```

Source: Martin Fowler, *Retroactive Event*, https://martinfowler.com/eaaDev/RetroactiveEvent.html

## 3. Compensating actions are domain-specific forward progress

The compensating-transaction literature emphasizes several points relevant to narrative custody:

- compensation need not restore the original state;
- it must account for work that happened after the original operation;
- domain rules decide what a meaningful correction is;
- high-impact or ambiguous decisions should include human review;
- original and compensating operations must be correlated and auditable;
- some side effects are irreversible.

That argues against a generic “move all consequences to the newest premise” rule. The correct repair may change the premise, dependent, relation, severity, rationale, or all of them. It may instead retire the dependency entirely. Lacuna exposes the debt and requires an authored choice.

Source: Microsoft Azure Architecture Center, *Compensating Transaction pattern*, https://learn.microsoft.com/en-us/azure/architecture/patterns/compensating-transaction

## 4. Reversal preserves history better than replacement deletion

Fowler’s accounting adjustment patterns contrast replacement adjustment, which deletes incorrect entries and loses direct history, with reversal/difference adjustments, which retain the old entries and append correcting records.

Lacuna’s projection resembles a semantic reversal-plus-successor:

- the predecessor remains in the ledger and historical projection;
- its active interval ends;
- a new consequence begins;
- a separate repair record connects them.

It avoids the clutter of synthetic opposite consequence links while preserving the reason and lineage that destructive replacement would lose.

Source: Martin Fowler, *Patterns for Accounting — Making Adjustments*, https://martinfowler.com/eaaDev/AccountingNarrative.html

## 5. Event sourcing favors compensating entries

Current event-sourcing guidance treats the event store as append-only and uses new entries to transition state rather than updating old history. The materialized projection may show an ended predecessor and active successor, but the authoritative correction is the appended event.

This supports three rev0150 decisions:

1. one `consequence.replaced` event owns all repair projection changes;
2. projection rebuild must reproduce the same chain;
3. verification must bind repair rows to origin event payloads, not merely check local table consistency.

Source: Microsoft Azure Architecture Center, *Event Sourcing pattern*, https://learn.microsoft.com/en-us/azure/architecture/patterns/event-sourcing

## 6. Reincorporation is not the same thing as causal agency

Tomaszewski's Marlinspike system selected scenes that reincorporated prior events and player actions. Human evaluation found that this produced more internally unified structures containing more of the players' significant actions, but players did not report a matching improvement in story quality or story-level agency.

That result is a warning for any retcon planner: making an action retrospectively necessary can manufacture *interpretive significance* without granting *causal influence*. Lacuna therefore treats a repaired consequence as authored custody, never as evidence that a player choice truly changed reachable outcomes. A future evaluation needs paired counterfactual runs, not merely a coherence score.

Source: Zach Tomaszewski, *On the Use of Reincorporation in Interactive Drama*, https://ojs.aaai.org/index.php/AIIDE/article/view/12468

## 7. Plot reflection demonstrates both the promise and the failure mode

Wu et al.'s Plot-based Reflection periodically adapts an incomplete plot chain from player-related memories. The paper explicitly bounds one reflection step because the model otherwise tends to over-adjust the plot. This is close empirical evidence for Gwern's broad intuition and for Lacuna's stricter substrate: adaptive replanning can improve perceived agency, but unconstrained reflection needs typed state, bounded changes, and a reviewable difference between what was observed and what was merely planned.

Lacuna's consequence replacement is intentionally smaller than plot reflection. It changes one explicit dependency edge, leaves predecessor and successor inspectable, and refuses to infer a whole revised world from fluent prose.

Source: Hongqiu Wu et al., *Towards Enhanced Immersion and Agency for LLM-based Interactive Drama*, ACL 2025, https://aclanthology.org/2025.acl-long.546/

## 8. Causal physics and narrative physics should not be one score

Shadow-Loom turns narrative into a versioned graphical world model and separates causal reasoning from narrative-effect scoring. It uses LLMs at extraction, rendering, and audit boundaries while typed code performs graph operations, intervention, and counterfactual reasoning.

That separation sharpens Lacuna's nonclaim. A consequence edge is not discovered causal physics; it is explicit authored dependency custody. A repair review can establish that a graph rewrite is structurally valid and properly authorized while remaining agnostic about dramatic quality. Future hosts may place a causal simulator and a narrative scorer above Lacuna, but neither should silently rewrite the ledger.

Source: David Wilmot, *Shadow-Loom: Causal Reasoning over Graphical World Models of Narratives*, 2026, https://arxiv.org/html/2605.02475v1

## 9. Truth-maintenance research favors explicit justifications

Doyle’s truth-maintenance work treats reasons and dependency-directed revision as first-class. De Kleer’s ATMS separates the problem solver, which proposes assumptions and justifications, from the maintenance layer, which tracks the contexts in which data hold. That is close to Lacuna’s intended division: an LLM may search and interpret, while the cube owns explicit custody and refuses inconsistent state.

De Kleer also warns that sound local maintenance can be undermined by a poorly controlled surrounding problem solver. Lacuna therefore does not treat lineage as proof: the planner must supply the justification, and the ledger can only preserve and validate what was supplied.

Lacuna is not a TMS and does not derive truth automatically, but the architectural lesson is decisive: revision quality depends on retaining why a record was supported, in which candidate context it held, and what depended on it. A mutable canon paragraph cannot answer those questions reliably.

Sources:

- Jon Doyle, *A Truth Maintenance System*, https://dspace.mit.edu/handle/1721.1/5733
- Jon Doyle, *Truth Maintenance Systems for Problem Solving*, https://dspace.mit.edu/handle/1721.1/6926
- Johan de Kleer, *Problem Solving with the ATMS*, https://dekleer.org/Publications/Problem%20Solving%20with%20the%20ATMS.pdf

## 10. Why a review should expose candidates but not choose

When an assignment is revised or an assertion is superseded, its explicit successor lineage is relevant evidence for repair. But three failure modes arise if the kernel auto-transfers:

- **semantic drift:** the successor changes the claim’s meaning or scope;
- **dependency drift:** the old relation no longer holds even though the endpoint has a successor;
- **severity drift:** the new dependence may deserve a different governance level.

Rev0150’s review lists active explicit descendants while keeping selection outside the kernel. This is a deliberate division of labor:

- the cube discovers lineage mechanically;
- the planner reasons about meaning;
- the replacement operation records the planner’s authored custody;
- tests and verification enforce structural integrity.

## 11. Why the digest binds to the atomic base head

A strict “any event appended before the reviewed operation stales the receipt” rule conflicts with source-bound turns. Committing narration responsibly requires first recording the narration source, then recording operations that cite it, all atomically.

The refined rule treats the change-set’s `expected_head` as the reviewed snapshot identity. During operation preparation, Lacuna recomputes the review using current in-transaction projections but substitutes the base head into the digest core.

This is analogous to optimistic concurrency at an aggregate boundary:

- outside writes after review are rejected;
- benign writes inside the same transaction can accompany the mutation;
- relevant in-transaction changes still alter the digest body and fail;
- no partial commit is possible.

The rule is intentionally narrow. A future multi-process host may add explicit review IDs or selective fingerprints, but rev0150 chooses one deterministic base-head contract.

## 12. Human improvisation suggests structure and agency are partners, not enemies

A 2025 study of paired human players and game masters found a strong positive link between participants’ perceptions of narrative structure and agency. It also frames bad agency experiences as failures of the improvisational partnership rather than as proof that structure itself is harmful.

That supports a key Lacuna design choice: the cube should not maximize surprise or flexibility by itself. It should give a human or model game master a legible shared state, explicit open obligations, and safe places to improvise. A repair frontier is therefore coordination material, not an automatic plot rewrite queue.

Source: Mira Fisher, Molly Siler, and Stephen G. Ware, *Structure, Agency, and Improvisation in Human-Led Digital Interactive Narrative Exercises*, AIIDE 2025, https://ojs.aaai.org/index.php/AIIDE/article/download/36827/38965/40904

## 13. Better-than-retcon implication

Gwern’s proposal optimizes hidden explanations after observing play. Lacuna’s emerging alternative is less about generating a clever new backstory and more about maintaining **typed revision custody**:

```text
plural worlds
+ explicit commitments
+ authored consequence edges
+ state-bound reviews
+ forward repair lineage
+ perspective-safe projections
```

A planner can still perform abductive search above this kernel. The difference is that it cannot make a new story look inevitable by silently moving every prior dependency. It must leave visible records of what changed, what did not, and which obligations remain.

Source under critique: Gwern Branwen, *Better Fiction via Retcon Planning*, https://gwern.net/blog/2026/llm-retcon

## Implementation consequences adopted in rev0150

- Add one-to-one `consequence.replaced` events and `consequence_repairs` projection.
- Require digest-bound repair review before replacement.
- Preserve predecessor and successor as separate consequence records.
- Validate the post-replacement graph, not the pre-replacement graph.
- Refuse new links to inactive endpoints.
- Bind repair projections to event payloads during verification.
- Expose review frontiers only to privileged planner contexts.
- Permit reviewed operations after benign source creation in the same atomic turn.
- Defer split/merge repair and automatic semantic transfer.

## Open research questions

1. Should repair authorization bind to a proposed candidate as well as the predecessor review?
2. How should one consequence split into several successors without turning repair into uncontrolled fan-out?
3. Can a host measure whether repairs preserve causal agency rather than merely retrospective significance?
4. What counterfactual probes reveal a repair that only works on the observed path?
5. When should a mystery engine cryptographically precommit to hidden facts and clue dependencies?
6. How should character motive continuity constrain repairs without freezing all interpretation?
7. Can diverse planner critics reduce shared rationalization failures when generating and scoring repair candidates?
