# PDF URL accession method

Rev0007 allows official DOJ-linked PDF URLs to be resolved and recorded without downloading, hashing, bundling, or summarizing the full document.

## Allowed

- record official URL;
- record content type and observed page count;
- record source page link id and line reference from the DOJ SLS page;
- record limited docket/header fields when needed for source identity;
- record a bounded document-effect atom only when the document family is clear.

## Not allowed

- no bundled PDF copies in this revision;
- no full text summaries;
- no officer/person/civilian extraction;
- no incident extraction;
- no current-status banner;
- no settlement amount extraction;
- no quotation-heavy public copy.

## Why no local PDFs yet

Public court and DOJ PDFs can contain names of attorneys, judges, agency personnel, officers, civilians, witnesses, public commenters, families, and other people. The archive may later store them under a stronger custody and privacy protocol, but rev0007 records locator/accession metadata only.
