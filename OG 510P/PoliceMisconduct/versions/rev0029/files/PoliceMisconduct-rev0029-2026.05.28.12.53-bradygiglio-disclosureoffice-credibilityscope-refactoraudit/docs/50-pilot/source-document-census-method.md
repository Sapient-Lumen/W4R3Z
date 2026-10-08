# Source-document census method

The document census is label-only.

## Admission rule

A document label may be admitted when a public carrier page lists it and the row can be tied to a matter object. The admitted claim is only:

> The source page listed a document label for this matter at this observation time.

It is not a claim about document contents.

## Why labels first

Document links move, DOJ pages change, PDFs get renamed, and some pages redirect. A label census preserves the public source topology before the cube tries to freeze every URL.

## Before summary

The next gate requires:

1. official URL captured;
2. access timestamp;
3. content-type recorded;
4. content hash if downloaded and retention is lawful/ethical;
5. document class confirmed;
6. privacy scan plan;
7. quote limits and summary template;
8. reviewer signoff.

## Public display

Public display of label-only census rows must use language like:

> DOJ source page lists these document labels. The cube has not yet summarized document contents or independently verified current court status.

## Failure modes prevented

- treating a `Findings Report` label as a live finding claim;
- treating a `Consent Decree` label as proof the decree remains active;
- treating a `Closed` label as a full legal-status history;
- exposing names from documents before privacy review;
- building officer lookup from federal pattern-or-practice documents prematurely.
