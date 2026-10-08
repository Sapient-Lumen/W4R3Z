# rev0016 conversation receipt

User asked to dive back in after the deep audit/factoring pass.

Builder decision: do not add famous cases yet. The audit identified higher-leverage structural debt: overloaded claim-support fields, unredteamed pattern candidates, non-normalized links, and uncontrolled source vocabulary. Rev0016 repairs those foundations without changing factual claim texts or record counts.

Main changes:

- every promoted record claim now uses `evidence_refs`;
- `CLAIM-STATUS-LEDGER.json` mirrors typed evidence references;
- every pattern candidate now has `red_team_controls`;
- `GRAPH-EDGES.json` gives a first queryable edge surface;
- `SOURCE-VOCABULARY-CONTROL-LEDGER.json` overlays source major classes;
- lint/audit were hardened to enforce the migration.

Guardrail: this revision is structural. It is not source revalidation, locator repair, second review, or case accretion.
