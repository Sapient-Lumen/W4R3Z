# Buddy-search request epoch design notes — rev0076

## Problem statement

A logical search tab can issue more than one network request. Recipient membership may change between sends, and responses may arrive late. Any source-binding design must say which request epoch a result belongs to.

## Candidate policies

| Policy | Wire token behavior | Recipient model | Advantage | Primary risk |
|---|---|---|---|---|
| A. New token per resend | allocate a fresh token for every network send; keep UI identity separate | one immutable set per wire token | clearest correlation and late-response semantics | requires lifecycle changes for aggregation, close/remove, ignored tokens, and UI ownership |
| B. Same token, replace set | reuse token; overwrite current recipients | latest send only | small state model | drops late replies from earlier intended recipients |
| C. Same token, union sets | reuse token; accumulate recipients | all recipients ever sent under token | preserves late replies | removed/stale names remain accepted and state grows |
| D. Same token, epoch list | reuse token; retain ordered recipient sets and timing metadata | explicit multi-epoch history | richest observability | result has no epoch identifier, so attribution remains ambiguous |
| E. Current compatibility | no recipient admission check | token/filter checks only | preserves existing mixed-client behavior | leaves local source-attribution mismatch |

## Preferred next experiment, not a selected patch

Policy A is the cleanest research direction because it makes the wire token itself the epoch identifier. It should be prototyped only after mapping:

1. logical search tab ownership versus wire-token ownership;
2. `SEARCH_TOKENS_ALLOWED` insertion and removal;
3. Search Again, wishlist, ignored-search, close-tab, and history behavior;
4. result aggregation across multiple tokens into one UI model;
5. late responses after replacement or closure;
6. compatibility with old clients whose response body usernames are unreliable.

A prototype must include a rollback/compatibility control. A green off-snapshot test alone is not enough.

## Reopening criteria for rev0040-style source filtering

A claimed-name filter can be reconsidered after an epoch policy exists and after its value is measured against false rejection risk. It still must not be described as authentication unless a server-bound identity mechanism is added and demonstrated.
