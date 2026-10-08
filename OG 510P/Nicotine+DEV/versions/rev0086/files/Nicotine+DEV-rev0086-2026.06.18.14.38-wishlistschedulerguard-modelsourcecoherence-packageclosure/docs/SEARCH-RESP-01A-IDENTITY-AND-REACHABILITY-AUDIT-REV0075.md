# SEARCH-RESP-01A identity and reachability audit — rev0075

## Audit question

Does accepting an off-request connection username prove unauthorized search-result injection, or only that the local response handler lacks a request-scope consistency check?

## Exact data flow

### 1. Local request construction

A user-mode `SearchRequest` stores its `users` collection. `do_peer_search()` sends a server `UserSearch(username, token, text)` for every requested username, using the same search token.

### 2. Server delivery

The protocol documents that the recipient receives a user search as a server `FileSearch` request. A matching recipient then opens or reuses a peer-message connection and sends `FileSearchResponse` with the original token.

### 3. Connection naming

For an incoming direct connection, `PeerInit.parse_network_message()` reads `init_user` from the wire and assigns it to `target_user` when no target was already known. Peer-message parsing later calls `_unpack_network_message(..., username=conn.init.target_user)`, which assigns that value to `msg.username`.

This is the value the rev0039 guard checks.

### 4. Payload naming

`FileSearchResponse` also begins with a username string, represented when sending as `search_username`. Exact-current parsing skips that username after reading its length and extracts the token. Upstream deliberately uses the connection's `PeerInit` username for search-result attribution because old Museek clients sent an incorrect payload username.

### 5. Handler admission

`Search._file_search_response()` checks:

```text
allowed token
existing, non-ignored search
ignored username
ignored username/IP pair
```

It does not compare `msg.username` to `search.users` for user-mode searches.

## Executable cases

| Case | Baseline | rev0039 guard | Interpretation |
|---|---|---|---|
| expected connection name, valid token | accepts | accepts | desired ordinary case |
| off-request connection name, valid token | accepts | rejects | confirmed local scope delta |
| empty expected set | accepts | rejects | guard fails closed for malformed/local empty scope |
| global search, arbitrary source | accepts | accepts | guard is mode-specific |
| wire `PeerInit` claims expected name | accepts | accepts | counterexample to authentication interpretation |
| payload name is wrong but `PeerInit` name is expected | accepts | accepts | preserves historical Museek compatibility workaround |

The identity counterexample uses the exact network-message parser, not a direct attribute assignment. It proves only that the checked name is wire-supplied. It does not claim to model every server/address check or a complete attack.

## Threat cases separated

### Honest or buggy off-request peer

The guard is effective. This is the strongest directly supported value proposition.

### Unrelated malicious peer using its own username

The guard rejects the response if the token is valid. This is defense in depth, but token acquisition and end-to-end delivery still require proof.

### Unrelated malicious peer claiming an expected username

The guard accepts the response. The obsolete `SendConnectToken` mechanism once allowed recipients to cross-check a username and non-zero token with the server, but current clients do not use it and the protocol says reintroduction would isolate a client.

### Requested peer returning arbitrary results

The guard accepts by design. It cannot establish that filenames, sizes, attributes, queue state, or availability claims from an expected peer are truthful.

### Legacy client with wrong payload username

The guard compares the connection name, so the 2021 compatibility workaround remains intact. This does not make the connection name authenticated.

## Token model

The current initial range contains about 4.3 million values, and subsequent allocations increment. This weakens any claim that the token is a cryptographic capability. It does not by itself prove that an unrelated peer can:

1. observe a nearby allocation;
2. know the number of intervening allocations;
3. race the intended response;
4. establish the necessary peer connection state;
5. cause a durable or meaningful outcome.

The token tests are intentionally labeled a model, not an exploit reproducer.

## Evidence ladder result

| Layer | Result | Missing before promotion |
|---|---|---|
| Parser acceptance | confirmed | none |
| Local request-scope mismatch | confirmed | none |
| Guard mechanics | confirmed | compatibility and value proof |
| Trustworthy source identity | not reached | server-bound or cryptographic binding |
| Practical token capability | partial only | observation/guessing and timing evidence |
| End-to-end injection | not reached | real network/state-machine reproducer |
| Measured security impact | not reached | reliable user or boundary harm |

The correct disposition is an open defense-in-depth question with no selected patch, not a production-ready security fix.
