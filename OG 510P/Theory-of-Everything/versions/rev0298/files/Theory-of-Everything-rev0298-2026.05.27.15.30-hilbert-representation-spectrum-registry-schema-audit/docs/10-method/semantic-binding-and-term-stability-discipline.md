# Semantic binding and term-stability discipline

Revision: `rev0272`

This surface makes terminology authority-bearing only after it is bound to executable rows. A word such as `observable`, `record`, `candidate`, `equivalence`, `duality`, `native`, `mechanism`, `reconstruction`, or `closure` does not carry the same meaning across every route. A route must name the controlled term, its preferred meaning, the prohibited equivocations, the public-versus-native bridge terms, the semantic-stability test, and the rollback handle before that term can affect authority.

## Stop rule

No route may use semantic, synonymous, equivalent, identical, native, observable, theoretical-term, public-term, dual, or same-candidate language unless `SEMANTIC-TERM-LEDGER.json` contains a current row for the route and the relevant claim binding names that row.

## Required separation

- **Label**: a human-readable string used in the archive.
- **Concept**: the controlled archive idea the label denotes.
- **Route term**: a concept whose meaning is fixed only inside a route denominator.
- **Public bridge term**: a term inherited from public records, data products, papers, measurements, or custody artifacts.
- **Candidate-native term**: a term licensed by the candidate's own route machinery.
- **Ontology predicate**: a stronger claim that the term refers to part of the candidate's physical furniture.

The archive uses this separation because controlled vocabularies and ontologies distinguish labels, concepts, mappings, and formal meaning, while philosophy of science distinguishes theoretical terms, observational bridge terms, and theory-internal meanings. See `REF-0269`, `REF-0270`, `REF-0271`, and `REF-0272`.

## Non-promotion rule

Semantic stability can prevent a false promotion, but it cannot create one. If a claim becomes stronger after a synonym swap, translation, dual-presentation restatement, or metadata rewording, the stronger claim is invalid until it passes the route state machine and the semantic/ontology/language-permission ledgers.
