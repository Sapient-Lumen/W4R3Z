# Source-page anchor map method — rev0014

A source-page anchor is an observation aid. It is not a preserved source and not a source claim.

The anchor map stores:

- source row ID;
- matter label;
- source-page status label as observed text;
- line-span hint from the web observation;
- document label count;
- link IDs already present in the census;
- the web observation reference;
- a full nonclaim block.

Anchor rows are intentionally fragile. Browser line numbers and link IDs can move. The stable matching keys are the matter label, document labels, source URL, later payload hashes, and source-version events.

Public display remains blocked until source capture, privacy review, missingness copy, and rollback dependencies exist.
