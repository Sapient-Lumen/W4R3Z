# Source-freeze protocol — rev0011

The source-freeze protocol separates four things that are often collapsed:

1. a citation exists;
2. a URL target resolves;
3. a payload has been preserved and hashed;
4. the payload content supports a claim.

Only the first two states exist broadly in the current cube. Rev0011 creates the work queue for states three and four while keeping state four closed.

## Required freeze receipt

A future content-carrying source accession must record:

- canonical URL;
- observed URL and redirect chain;
- retrieval timestamp in UTC;
- HTTP status or access result;
- content type;
- byte length when available;
- SHA-256 payload hash when payload is captured;
- source page or docket context;
- operator/tool identifier;
- privacy scan state;
- redistribution/public-display state.

## Nonclaim discipline

A freeze receipt cannot by itself create:

- a misconduct claim;
- a current legal-status claim;
- an officer/person record;
- a civilian/witness/family record;
- a lawsuit-merits record;
- a settlement amount;
- a denominator/rate display.
