# Rev0004 document census report

Rev0004 converts the DOJ SLS law-enforcement source-row pilot into a controlled document inventory without admitting document-content claims.

## What was admitted

- `27` matter objects derived from the DOJ SLS law-enforcement source rows.
- `148` label-only source-document census rows.
- `34` source-scoped status events and fragility flags.
- `7` spot-checked official URLs.

## What was not admitted

- no officer records;
- no civilian records;
- no incident records;
- no lawsuit merits records;
- no settlement amount records;
- no current court-status assertions;
- no document-content summaries.

## Why this matters

The seed wants a national, normalized, jurisdiction-spanning police accountability corpus. The premature version of that project would jump from public documents to claims about officers or incidents. Rev0004 takes the opposite path: it makes the source graph richer while reducing claim power.

The new model says: **source page → matter object → document label → frozen document → privacy scan → bounded summary → source-bound claim**.

Rev0004 opens only the first three steps, and only as nonclaims.

## Matter object

A matter object is the unit between a source page row and a department page. It records the public carrier's label, the agencies named in the row, the source-page status label, the document-label count, and the warnings required before public display.

Matter objects are useful because a DOJ row may not map cleanly to one department. Examples now tracked:

- mixed agencies and mixed statuses;
- sheriff offices rather than municipal police departments;
- territories;
- specialized units and subunits;
- consent-decree lifecycle states such as sustainment, partial termination, termination motion, and closing letter.

## Document census entry

A document census entry is intentionally weak. It records a label such as `Findings Report (2023)` or `Consent Decree (2025)` as a source-page observation. It does not assert what the document says.

The census does allow the next revision to prioritize URL freezing. It also prevents future operators from losing the shape of the source page when linked documents move or disappear.

## Status policy

Status labels now have four separate concepts:

1. `source_page_status_label`
2. `document_chain_status_signal`
3. `court_order_status`
4. `current_status_candidate`

Only the first two exist in rev0004, and both are display-limited. The cube does not claim current legal status without docket/current-source review.

## Missingness

The project now explicitly records what it has not done. In rev0004, the big missing surfaces are:

- most official URLs are not frozen;
- no document content hashes exist;
- no current dockets were checked;
- no independent monitor archive was crawled;
- no privacy scan has occurred;
- no department denominator source has been joined.

This is intentional. Missingness is part of truthfulness.
