# Structural audit — rev0269

## What was inspected

The rev0268 ZIP was unpacked and checked for package structure, numbered-file continuity, citation-footer placement, open-question structure, source-register structure, and source usage.

## Main findings

1. The numbered archive was complete from `00` through `300` before this revision.
2. The archive had become coherent but addenda-heavy: many files contained material after the standard citation footer.
3. `05-open-questions.md` contained a structural defect: questions 56 and 57 were plain text under question 55, and the citation footer appeared before later addenda.
4. `sources/register.md` contained the citation-rule block mid-register, between source entries.
5. The service-continuity family from `273` through `300` had become a hidden template.
6. The most useful next step was therefore schema, not another unstructured addendum.

## Repairs made

- Added `301` as the datacube schema doctrine.
- Added `302` as the service-continuity admission template.
- Added `303` and `304` for public-safety continuity and response-overload shock absorption.
- Added `305` for coastal-ocean continuity.
- Added `306` for thermal survivability.
- Added `307` for carbon-market and offset-claim quarantine.
- Added `/cube/schema.json`.
- Added `/cube/index.csv` as a first-pass index over numbered files.
- Added `/cube/service-continuity-template.md`.
- Moved citation footers to the true end of markdown files where a footer existed before later addenda.
- Repaired `05-open-questions.md` question headings and added rev0269 open questions.
- Moved the source-register citation rule to the top of `sources/register.md`.

## Not fully solved

- Existing source duplication was not deleted because old source IDs are already referenced throughout the archive. A future source-deduplication pass should add aliases and `supersedes` fields before removing anything.
- Legacy files do not yet contain YAML front matter. rev0269 deliberately uses an external cube index first to avoid noisy mass rewrites.
- The cube index is a first-pass retrieval layer, not a final ontology. Tags should be sharpened when files are next materially revised.

## Admission rule after rev0269

A future file should be admitted only if it adds a new service floor, shock cascade, control point, proof ledger, integrity gate, clock conflict, or compression that makes the archive easier to use.

## Final rev0269 packaging check

- Numbered Markdown files now run from `00` through `307` with no gaps.
- `cube/index.csv` indexes 308 numbered files as a first-pass external datacube.
- Citation footers in top-level numbered Markdown files were normalized so the footer closes the file rather than appearing before later addenda.
- `sources/register.md` now holds the citation-rule block near the top and adds `S536`–`S546` for rev0269.

Remaining work intentionally left open: backfill full YAML front matter only as files are materially revised; deduplicate near-duplicate source-register entries by adding canonical-source IDs rather than deleting history blindly.
