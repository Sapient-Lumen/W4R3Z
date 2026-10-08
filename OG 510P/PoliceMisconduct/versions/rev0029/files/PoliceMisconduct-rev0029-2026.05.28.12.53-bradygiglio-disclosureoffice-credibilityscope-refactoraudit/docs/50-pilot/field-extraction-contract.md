# Field extraction contract

Rev0003 does not yet permit document summaries, but it defines the extraction contract that future summaries must obey.

## Before extracting any document field

The operator must know:

- document class;
- issuer;
- date/effective date;
- source row;
- whether the document is a pleading, finding, order, agreement, monitor report, closing letter, or summary;
- whether the document names civilians, witnesses, minors, survivors, families, or officers;
- whether the source text has later correction, retraction, amendment, termination, or appeal status.

## Claim-state examples

A complaint can support:

- “A complaint was filed alleging X.”

It cannot by itself support:

- “X happened.”

A consent decree can support:

- “The parties/court adopted obligations Y.”

It cannot by itself support:

- “The department admitted Y,” unless the text says so.

A findings report can support:

- “DOJ stated reasonable cause/belief/findings according to the report.”

It cannot by itself support:

- “A named officer committed misconduct,” unless the document and claim state specifically support that and identity/privacy gates open.

A closing letter can support:

- “The issuing body closed the matter or stated closure under specified terms.”

It cannot erase:

- the existence of earlier public source records.
