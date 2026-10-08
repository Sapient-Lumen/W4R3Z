# Remedy-hardening-attestation verdict-legitimacy lineage receipt page — adjudicator authority, burden, threshold, and blocked stronger sentences

## Purpose

This page is the durable one-receipt summary for adjudication legitimacy after witness trust review.
It lets a later operator read one artifact and know exactly whether the trusted witness set merely suggests the sentence, actually meets the active burden, or still fails legitimacy because the rulebook, authority, tie-break, or override state leaves the stronger sentence blocked.

## Receipt fields

- receipt identifier
- verdict-legitimacy identifier
- source observer-integrity receipt identifier
- current rulebook identifier and version
- target sentence reviewed
- authorized adjudicator summary
- burden and threshold summary
- tie-break and override summary
- admitted evidence summary
- excluded evidence summary
- current verdict-legitimacy class
- highest honest verdict sentence
- blocked stronger sentence
- evidence and rulebook references
- issued-at timestamp

## Primary sentence block

The receipt must begin with exactly two lines:

- **Highest honest verdict-legitimacy sentence**
- **Blocked stronger sentence**

## Required sections

1. **Why this sentence is or is not legitimate under the active rulebook**
2. **Which adjudicator, burden, and threshold governed the case**
3. **Which trusted evidence counted and which did not**
4. **Whether tie-breaks, overrides, or version drift still matter**
5. **Why the next stronger sentence is blocked**

## Hard rules

The receipt must never let:

- `trusted evidence exists` impersonate `the verdict is legitimate`
- `this surface looks green` impersonate `the burden for the stronger sentence was met`
- `one current world` impersonate `all relevant worlds and versions`
- `queue looked ordered` impersonate `decision rule proved`
- `a reviewer looked at it` impersonate `authorized ratification happened`
