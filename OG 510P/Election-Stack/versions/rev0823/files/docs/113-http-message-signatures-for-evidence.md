# HTTP message signatures for evidence

**Track:** A (Deployable core)


## Problem
CDNs, relays, and caching proxies complicate “what did the server actually say?” disputes.

## Solution
Sign HTTP responses at the application layer:
- include a signature covering key headers + body digest
- include the pinned checkpoint/bundle hash

This lets verifiers confirm authenticity even when transport is mediated.

## Normative requirements
- **SHOULD** sign evidence API responses and status page JSON.
- **MUST** include the hash of the relevant evidence object in the signed material.
- **MUST** publish verifier tooling for signature checking.

## Reference
HTTP Message Signatures (RFC 9421) (`source: rfc9421_txt`).