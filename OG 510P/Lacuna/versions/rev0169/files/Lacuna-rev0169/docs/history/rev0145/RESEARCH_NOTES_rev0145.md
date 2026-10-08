# Research notes — rev0145

This revision used external research as design pressure, not as an excuse to import an entire framework.

## Assumption-based truth maintenance

Johan de Kleer's work on the Assumption-based Truth Maintenance System models propositions under multiple environments rather than forcing one global belief set. That is the clearest ancestor for retaining several candidate worlds and asking which assumptions support each conclusion.

Design consequence: Lacuna stores world-local assignments and does not collapse the preferred world into global canon.

Source: Johan de Kleer, “Problem Solving with the ATMS.”  
https://dekleer.org/Publications/Problem%20Solving%20with%20the%20ATMS.pdf

## Provenance

The W3C PROV ontology separates entities, activities, and agents and supplies a vocabulary for derivation and attribution. Lacuna's current source/assertor/event model is intentionally smaller, but it follows the same discipline: a proposition's content is not its provenance.

Design consequence: sources and agents receive stable IDs; assertions can point to both; event custody is separate from semantic content.

Source: W3C, “PROV-O: The PROV Ontology.”  
https://www.w3.org/TR/prov-o/

## Bitemporal data

Temporal database literature distinguishes valid time—when a fact holds in the modeled domain—from transaction time—when the database records it. Fiction and simulations need the same distinction because revelations often concern earlier events.

Design consequence: ledger sequence/recording time and narrative `timeline_id`/valid intervals are separate axes.

Source: Christian S. Jensen et al., “A Glossary of Temporal Database Concepts.”  
https://sigmodrecord.org/publications/sigmodRecord/9209/pdfs/140979.140996.pdf

## Particle filtering and hypothesis populations

Sequential Monte Carlo methods represent uncertain state with weighted particles that survive, lose weight, or are resampled as observations arrive. Lacuna does not implement Bayesian filtering in rev0145, but the analogy argues strongly against storing one winning hidden world.

Design consequence: several weighted worlds remain explicit; selection is a status, not ontological promotion.

Source: Arnaud Doucet and Adam M. Johansen, “A Tutorial on Particle Filtering and Smoothing.”  
https://web-static-aws.seas.harvard.edu/courses/cs281/papers/doucet-johansen.pdf

## Belief revision and minimal change

Belief-revision theory treats incorporation of new information as a constrained revision problem rather than permission to rebuild everything. The principle of informational economy supports explicit commitments and additive supersession.

Design consequence: events remain immutable; assertions are ended or superseded; anchors block convenient reinterpretation.

Source: Peter Gärdenfors, “Belief Revision: An Introduction.”  
https://www.lucs.lu.se/fileadmin/user_upload/project/lucs/PG/pg-1992d.pdf

## Narrative antecedents

The immediate product stimulus was Gwern Branwen's “LLM Retcon,” which proposes repeatedly inferring hidden explanations and future rollouts from observed canon. The useful inversion is to delay hidden commitments. The failure mode is treating a prose canon summary as an adequate state representation or repeatedly replacing one hidden world with another.

Design consequence: Lacuna is the missing substrate under such a planner—an epistemic ledger plus multiple candidate worlds. It intentionally does not perform the planner's dramatic scoring itself.

Source: Gwern Branwen, “LLM Retcon” (2026).  
https://gwern.net/blog/2026/llm-retcon

## Research synthesis

The combined design is:

```text
ATMS-style environments
+ provenance discipline
+ bitemporal custody
+ particle-like world plurality
+ minimal-change revision
= an epistemic ledger, not a canon paragraph
```

The open research question is not whether an LLM can invent a coherent explanation. It is whether a system can preserve causal agency, character identity, fair evidence, and adjacent counterfactual consistency while adaptively delaying commitments. Lacuna rev0145 builds the state layer needed to test that question.
