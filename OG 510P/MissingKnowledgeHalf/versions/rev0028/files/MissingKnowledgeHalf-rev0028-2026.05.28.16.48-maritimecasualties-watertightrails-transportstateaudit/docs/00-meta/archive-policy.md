# Archive policy

## Package policy

This cube is text/JSON first. It should not retain bulky PDFs, datasets, screenshots, or prior-art bundles unless a future revision has a specific legal/ethical reason and a storage policy. Prefer stable source pointers, hashes, archive links, and extracted summaries.

## Canonical homes

Every durable concept should have one home:

- record schema: `docs/20-schema/` and `schemas/`
- status/evidence method: `docs/10-method/evidence-severity-and-status.md`
- source acquisition: `docs/10-method/source-acquisition-protocol.md`
- ethical handling: `docs/10-method/ethical-handling.md`
- candidate records: `CANDIDATE-CASE-QUEUE.json`
- source memory: `SOURCE-ACQUISITION-LEDGER.json`
- release state: `SURFACE-STATUS.json`, `RELEASE-MANIFEST.json`, `REVISION-RECEIPT.json`

Avoid duplicate conceptual homes. If a later revision moves a concept, leave a pointer and update the receipt.

## Head semantics

- **Bundle head**: the packaged revision currently linked to the user.
- **Operational head**: the archive state future work should continue from.
- **Citation head**: the highest revision containing source-backed records that can be cited as corpus content. In rev0001, citation head is intentionally `none-yet-primary-source-records-not-admitted`.

## Promotion policy

A case can move from candidate to record only when it has:

1. stable record ID,
2. exact claim or incident/influence statement,
3. at least one source record,
4. evidence class,
5. source permanence metadata,
6. status token and status rationale,
7. sensitivity class,
8. links to related records or explicit note that links are pending,
9. revision receipt entry.

## Quarantine policy

Use quarantine for:

- seed-only case mentions,
- speculative categories,
- ethically sensitive candidates before handling rules are clear,
- contested claims without adequate source review,
- alluring summaries that are not yet grounded.


## rev0004 head semantics

`rev0004` is the first cross-lane source-backed head. It admits one replication-program record and four medical negative-result/reversal records, while keeping both new and old pattern records at candidate level. The citation head is no longer empty, but every promoted record remains one-pass reviewed and incomplete.

Records may be cited only at their stated grain. `MKH-REP-0005` is a program-level replication record, not a child study-pair record. `MKH-NEG-0009` through `MKH-NEG-0012` are trial/reversal records scoped to named interventions, populations, and endpoints, not general medical advice or blanket rejection of whole treatment families.
