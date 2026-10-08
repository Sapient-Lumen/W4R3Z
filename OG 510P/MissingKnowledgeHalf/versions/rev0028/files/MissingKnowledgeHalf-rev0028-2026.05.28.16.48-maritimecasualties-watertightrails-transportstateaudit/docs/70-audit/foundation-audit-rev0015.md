# rev0015 foundation audit — deep structural pass

This revision is not a case-accretion revision. It audits the cube as infrastructure: records, ledgers, schemas, source locators, claim graph, handoff surfaces, factor axes, and future-session resumption.

The seed says the unified corpus should be the structured record of how human knowledge gets things wrong and what changes when it does. That means the cube must remember not only cases, but also correction surfaces, status motion, practice lag, transmission, and source permanence. Rev0015 checks whether the foundation can support that job.

## Scope

Audited surfaces:

- promoted record index and all promoted record files;
- claim IDs and claim-status ledger coverage;
- source references, source permanence coverage, and source payload shape;
- schemas and lint behavior;
- revision receipts and context-pack handoff surfaces;
- weak locator language;
- factor axes and record-type pressure.

Not done in this revision:

- full web/link-rot verification of all 140 URLs;
- second-review factual re-extraction of all 294 claims;
- expert review;
- pattern maturity promotion.

## Findings

The foundation is better than expected in graph coherence: record IDs resolve, sources exist, claim IDs are contiguous, and source permanence entries exist for every source record.

The foundation is weaker than it looked in schema closure: the source-record schema did not match actual source files, unified links had incompatible shapes, and eleven rev0013 records lacked unknowns/next_actions under the hardened non-source record rule. Rev0015 repairs these specific problems and makes jsonschema validation part of lint.

The most important unresolved issue is semantic factoring. Current record types are useful, but they are being asked to carry too much. The cube needs factor axes: object role, evidence surface, status motion, denominator visibility, correction surface, transmission edge, practice status, harm/ethics, pattern maturity, and review depth.

## Decision

Keep the current readable record files. Do not prematurely explode everything into tiny graph nodes. But from here forward, every scaling move should know which factor axis it advances.

