# Roster membership review page: ever-seen, online, disconnected, hidden, and self-derived branches interface spec

## Problem this page solves

A participant row can mean several different things:

- live and reachable now
- offline but still a known roster member
- auto-expired or disconnected after dormancy
- hidden from the list for decluttering only
- self-derived local branch that does not add remote resilience
- disconnected linked-folder visibility row with no current path or bytes

When those meanings are collapsed, the operator cannot tell whether the roster is a coverage map, a memory ledger, or just a cluttered mixture of both.

## Review trigger

Open this page whenever any of the following are true:

- the subject publishes `X of Y peers`
- the operator asks whether there is enough redundancy
- the roster contains gray, hidden, or disconnected rows
- local shares or linked-device branches make the count look larger than the real independent cohort
- a troubleshooting path depends on whether a missing source is truly absent or only detached / hidden / historical

## Fixed review order

### A. Count sentence under review

Show:

- current public sentence being challenged
- displayed count
- screen / API surface that emitted it
- why the sentence may overstate or understate reality

### B. Membership buckets

Bucket every row into exactly one primary bucket:

- `live-independent`
- `live-self-derived`
- `offline-known`
- `disconnected-gray`
- `hidden-offline`
- `visibility-only-disconnected`
- `severed-no-longer-member`
- `unknown`

The page must never leave a row uncategorized.

### C. Automatic-return analysis

For every non-live row, publish:

- can it return automatically?
- does it require a new approval?
- was it hidden only, disconnected by timeout, or severed by explicit action?
- would its return change source coverage, only row visibility, or both?

### D. Independence analysis

For every live row, publish:

- independent remote seat or self-derived local branch
- source of data for this row
- whether it can seed other remote peers directly
- whether it merely fans out the same parent source locally

### E. Safer replacement sentences

Generate three sentences:

1. **visible-row sentence**
2. **live-set sentence**
3. **independent-source sentence**

Example:

- `7 rows are visible in the cohort history.`
- `3 rows are live now.`
- `2 live rows are independent source-capable peers; 1 additional live row is self-derived local fanout.`

## Review outputs

The page must produce:

- revised counts by bucket
- automatic-return map
- independence map
- source-capability warning if only one independent source remains
- one `blocked stronger sentence`

## CLI / API hints

- `anonsync cohort review --subject vault --basis visible-rows`
- `anonsync cohort review --subject vault --split independence`
- `anonsync cohort review --subject vault --show auto-return`

## Hard rules

- `ever seen` may never be rendered as if it were `live now`
- `hidden` may never be rendered as if it were `removed`
- `live` may never be rendered as if it implied `independent`
- `count > 1` may never be rendered as if it implied `multi-source resilience`
