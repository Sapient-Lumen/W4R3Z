# SEARCH-RESP-01A current disposition — rev0075

## Decision

The exact-current behavior is real, but the historical security and production-readiness conclusion was too strong.

```text
confirmed behavior:
  a FileSearchResponse with an allowed token is accepted for a user-mode search
  even when msg.username is not in that search's requested user set

confirmed patch mechanics:
  the rev0039 guard rejects off-set names and preserves expected names

failed security inference:
  msg.username is populated from the username claimed in wire PeerInit
  an expected-name claim passes the guard without authenticating the peer

current disposition:
  confirmed local request-scope consistency gap
  open defense-in-depth research
  selected patch: none
  private security route: not supported by current evidence
```

Historical rev0039 files named `PRODUCTION-GATE`, `PRODUCTION-READY`, and `SELECTED-PATCH` remain provenance. They are superseded as current disposition authority.

## Exact-current result

```text
source lane: github-branch-3.3.x
source ref: 98089ac233aa57786e8dbdc48123f6ac1c4767d8
source invariants: 8/8 pass
classified source-state/test-role expectations: 8/8 pass
compile checks: 6/6 pass
isolated upstream units:
  baseline: 58 passed, 1 skipped
  rev0039 guard: 58 passed, 1 skipped
  i18n excluded in both states because msgfmt is unavailable
selected patch: none
```

The matrix uses expected failures to distinguish observed behavior from desired policy:

| Source state | Current behavior | rev0039 policy | Identity counterexample | Token model |
|---|---:|---:|---:|---:|
| Baseline | 2 pass | 2 pass / 2 expected fail | 3 pass | 2 pass |
| rev0039 guard | 1 pass / 1 expected fail | 4 pass | 3 pass | 2 pass |

The guard therefore does what its tests ask. That fact does not establish that it authenticates a response source or materially closes a security boundary.

## Four values the old packet conflated

A direct user search has four distinct values:

1. `search.users`: the usernames the local requester intended to search;
2. `msg.username`: the connection username assigned from `conn.init.target_user`;
3. `FileSearchResponse.search_username`: the username inside the compressed response payload;
4. `msg.token`: the client-generated search correlation token.

The current handler checks the token, search existence, ignore state, and network filters. It does not compare item 1 with item 2. The historical guard adds that comparison.

However, item 2 is derived from `PeerInit.init_user` on an incoming direct connection. The protocol's old server-mediated username/token cross-check is obsolete and unusable across today's network. The comparison is therefore a scope-consistency filter over a claimed name, not proof of peer identity.

## Why the gap is still worth keeping open

The server routes a `UserSearch` to the requested user, and the intended response is that user's `FileSearchResponse`. There is no identified legitimate reason for an honest unrelated username to satisfy that direct user search. A source-set check can therefore have defense-in-depth value:

- it rejects accidental or buggy off-request responses;
- it rejects a malicious peer that uses its own off-request username;
- it documents the local request/response invariant.

It does not reject a peer that claims one of the expected names in `PeerInit`, and it does not constrain the requested peer from returning arbitrary filenames or metadata. Those limitations are decisive for security severity.

## Compatibility evidence

Upstream commit `5e3e8fcd1d4fa1965976fd29595784a4dcaad3d6` deliberately stopped trusting the username inside `FileSearchResponse`. Its commit message says old Museek clients sent the wrong payload username, so Nicotine+ uses the username associated with the peer connection instead.

The rev0039 guard preserves that payload compatibility because it compares the connection name. The new counterexample also shows the cost: connection naming is the weaker, spoofable boundary. Current upstream hardening in other subsystems explicitly acknowledges that Soulseek username spoofing cannot be fully prevented.

This history argues neither for accepting every off-scope result nor for calling the guard an authentication fix. It explains the tradeoff that the old packet skipped.

## Token reachability and impact

Exact-current source initializes tokens in `0..UINT32_LIMIT // 1000` and increments them linearly. A previously observed token can therefore predict the next allocation when no intervening allocation occurs. Rev0075 records this only as a bounded model.

Missing evidence includes:

- a practical way for an unrelated peer to observe or guess the live token in time;
- a successful end-to-end injection over the real connection state machine;
- reliable attribution or connection reuse after a spoofed `PeerInit`;
- measured user-visible harm beyond displaying an untrusted search result;
- impact distinct from a requested peer returning arbitrary results itself.

No exploitability or security-severity claim follows from token structure alone.

## What would change the disposition

A patch could become selected research policy after all of the following are established:

1. compatibility tests cover exact username semantics, case/canonicalization, reconnects, and mixed clients;
2. the guard has measurable value against a reachable class of off-request responses;
3. the documentation states explicitly that it is not authentication;
4. focused and integration tests cover parser rejection, result display, connection cleanup, and repeated searches.

A private security route would require the additional attacker-capability and impact evidence listed above.

## Authority and boundary

Current machine-readable authority is `data/current_packet_dispositions.json`. All generated patches, tests, reports, and prose in this cube are research-only and are not upstream contribution material.
