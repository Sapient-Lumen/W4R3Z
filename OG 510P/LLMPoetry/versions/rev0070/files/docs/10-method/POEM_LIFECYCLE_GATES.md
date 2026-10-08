# Poem lifecycle gates

`template` → `preflight` → `draft` → `cold_review_ready` → `graveyard` or `anthology_candidate` → `evidence_candidate` → `admitted` or `withdrawn`

## Gate requirements

- **preflight**: metadata exists; pilot or form intent recorded; no poem text required.
- **draft**: text exists; generation context recorded; same-turn judgment forbidden.
- **cold_review_ready**: at least one later turn has begun; drafting rationale stripped from judge packet.
- **anthology_candidate**: cold review passed; obvious metrics and banlist scan run.
- **evidence_candidate**: quote-search receipts, source/claim receipts if factual, constraint receipts if formal, disclosure-test plan.
- **admitted**: survives hostile review, disclosure obligations, and project-owner acceptance.

A poem can always move to `graveyard` with a coroner note. Graveyard is a teaching hospital, not a trash folder.


## rev0012 note

The human selected high-risk machine-native work. P0001 now exists as `draft_001` using `FORM-branch-selector-diptych`; it is unjudged and cannot be promoted in the drafting turn.
