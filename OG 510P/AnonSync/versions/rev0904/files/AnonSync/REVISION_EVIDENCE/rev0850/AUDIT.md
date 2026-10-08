# AnonSync rev0850 audit

## Audit target

This revision audits SQLite authorizer context lifetime as a dependency-ordered
authority protocol. The reviewed transition is:

1. own one exact serialized SQLite connection generation;
2. publish the connection-authority state as client data;
3. attach a second named client-data claim for the authorizer context;
4. install the singleton authorizer callback;
5. prove callback identity with an executable nonce challenge;
6. serialize every use and replacement under the connection mutex;
7. reject revocation across probes, permits, savepoints, or transactions;
8. disable the callback;
9. synchronously destroy the authorizer lifetime claim;
10. destroy the connection-authority context; and
11. strictly close the typed database owner.

## Findings corrected

### Critical: client-data destruction could free a retained authorizer context

`ConnectionAuthorityState` was both SQLite-owned client data and the
`sqlite3_set_authorizer()` context. The client-data destructor deleted it
without first disabling the authorizer. Because SQLite invokes that destructor
on same-name replacement or close and does not promise close-time destructor
ordering, the old code could leave SQLite with a dangling callback context.
Rev0850 gives the callback its own lifetime sentinel and makes state destruction
while that sentinel is live a fail-stop violation.

### High: typed database close did not consume authorizer authority

The handle slot enforced strict `sqlite3_close()` but did not revoke the
connection authorizer first. The new close hook enters the exact FULLMUTEX
connection, validates state/process/generation shape, rejects active boundary
state, detaches the authorizer owner, and only then clears the state client-data
slot. Typed owner destruction invokes this hook before close.

### High: raw setter ownership was distributed across the state monolith

Authorizer installation and supersession were direct calls in the broad
connection-authority translation unit. All production setters now reside in a
157-line focused owner with a separately linked 20-check runtime corpus. The
broad state machine consumes attach/replace/detach transitions instead of
spelling raw registration.

### Medium: duplicated audits had become a change amplifier

The historical 332-line authorizer audit and newer ownership rules were
independent sources of truth. The old command name is retained for compatibility
but now delegates to the registered focused audit in 13 lines. The transaction
stack audit follows typed owner operations, so raw setter movement cannot make
one audit silently stale while another passes.

## Executable evidence

- focused owner: **20/20** checks;
- integrated connection authority: **141/141** checks;
- transaction exception composition: **37/37** checks;
- allocator-fault campaign: **642/642** checks, 318 isolated workers and 312
  injected cutpoints;
- process/fork authority: **44/44** checks;
- peer-ingress schema authority: **66/66** checks;
- direct focused total: **950/950** under GCC, Clang 17 `-Werror`, and GCC
  ASan+UBSan with leak detection;
- repeatability: owner 100/100 and integrated authority 50/50;
- registered suite: **147/147**, including **43/43** registered audits.

The integrated fresh-image probes terminate on immediate raw close and on
same-name replacement of the live connection-authority state. The ordinary
teardown test proves both client-data slots are absent before close, rejects the
stale proof, and confirms a fresh state restarts local authorizer generation 1.
The cross-thread close test proves revocation waits behind a retained exact
mutex capability.

## Structural evidence

- exact production `sqlite3_set_authorizer()` inventory:
  `src/persistence/sqlite_authorizer_owner.cpp` with three calls;
- authorizer owner audit: **30/30**;
- transaction-stack authority audit: **100/100**;
- process authority: **89/89**;
- mutex capability: **70/70**;
- self-exec process: **36/36**;
- inherited process: **15/15**;
- raw fork boundaries: **11/11**.

## Remaining architectural risk

A client-data claim is a destruction witness, not a general callback registry.
Busy, progress, and authorizer owners still coordinate through separate named
slots and surrounding conventions. The next architectural reduction should put
all singleton SQLite callback slots under one exact-generation connection
registry, with one close protocol and explicit slot generations. That should be
paired with race-oriented testing rather than another lexical audit layer.

SQLite does not expose the current authorizer callback, so continuous identity
proof is impossible without controlling every setter. The nonce probe proves
identity at reviewed use boundaries; source inventory confines production
setters. This is stronger than trusting client-data presence but is not a claim
against arbitrary in-process hostile native code.
