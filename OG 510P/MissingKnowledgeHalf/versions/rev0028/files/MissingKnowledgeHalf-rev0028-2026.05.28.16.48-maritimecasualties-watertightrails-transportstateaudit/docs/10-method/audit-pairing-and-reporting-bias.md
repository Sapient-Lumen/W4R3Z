# Audit pairing and reporting bias

Revision: `rev0009`.

Rev0008 created denominator-visibility infrastructure records. Rev0009 adds the method rule that visibility claims should be audited by pairing two surfaces:

- a **denominator surface**: FDA review packages, approved protocols, trial registries, ethics/inception cohorts, or another source that can show what existed before publication; and
- a **published numerator surface**: journal articles, public abstracts, indexed publications, review-included studies, or other literature that ordinary readers can see.

The file drawer becomes empirical when those two surfaces fail to match.

## Required state distinctions

Do not collapse these into one flag:

1. Study never published.
2. Study delayed before publication.
3. Study published but not linked to its registry/protocol.
4. Study published but measured outcomes are omitted or incompletely reported.
5. Study published but primary outcomes are changed, introduced, or omitted.
6. Study published but framed differently from a regulator/protocol conclusion.
7. Study published transparently with null or negative findings.

## Method warning

Funnel plots, fail-safe counts, and other statistical diagnostics may help as sensitivity tools, but they cannot substitute for source acquisition. A MissingKnowledgeHalf record should first ask: **what denominator surface lets us know what was done?**

## Ethics warning

Reporting gaps are evidence-system facts before they are personal accusations. The default explanation should be structural unless a source directly supports a narrower claim.
