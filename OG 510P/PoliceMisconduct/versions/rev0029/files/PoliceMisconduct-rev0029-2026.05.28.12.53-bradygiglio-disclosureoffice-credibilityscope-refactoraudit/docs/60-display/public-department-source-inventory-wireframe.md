# Public department source-inventory wireframe v0

This is a display design, not a live page.

## Header

Department / agency label

- Source inventory only
- No officer lookup in this release
- Source-page labels are not current legal-status claims

## Source matter cards

Each card may show:

- DOJ matter label
- agencies named by DOJ
- source-page status label with observation timestamp
- document-label count
- document classes present
- status fragility flags
- missingness warnings

Each card must not show:

- named officer lists
- civilian names
- incident narratives
- settlement dollar amounts
- risk scores
- unreviewed document summaries

## Document label accordion

Closed by default. When opened:

- document labels listed by source page;
- year labels where present;
- document class;
- URL-freeze state;
- privacy-scan state.

A warning appears above the accordion:

> These are source-page document labels, not document summaries. The cube has not yet extracted or validated document contents.

## Status display

Preferred copy:

> DOJ source-page status label: Enforcement. Last observed by cube: [timestamp]. This label is source-scoped; current court status requires separate verification.

For fragile rows:

> Status history is complex. DOJ page label and document-chain signals may not resolve to a single current status without docket review.

## Correction / reply route

Every source-inventory card needs a correction route for agencies, community organizations, journalists, families, and affected people. Corrections should create review tickets, not silent edits.
