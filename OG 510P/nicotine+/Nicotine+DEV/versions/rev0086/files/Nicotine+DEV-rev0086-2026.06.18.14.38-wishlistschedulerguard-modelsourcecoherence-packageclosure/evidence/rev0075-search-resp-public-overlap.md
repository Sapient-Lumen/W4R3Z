# SEARCH-RESP-01A bounded public-context review — rev0075

Checked 2026-06-18 America/New_York against official Nicotine+ project pages and the supplied current Git history.

## Supported source and protocol

- The project security policy identifies `3.3.x` as the supported release series.
- The exact supplied branch head is `98089ac233aa57786e8dbdc48123f6ac1c4767d8`.
- The protocol says a `UserSearch` recipient receives a `FileSearch` request and that a `FileSearchResponse` carries the original search token.
- The protocol says `PeerInit`'s token is zero and ignored today.
- The obsolete `SendConnectToken` message once allowed a recipient to cross-check username and token to reject spoofed connection attempts; current client adoption makes reintroduction unusable because it would isolate the client.

## Adjacent history

- Commit `5e3e8fcd1` intentionally uses the `PeerInit` connection username because old Museek clients sent a wrong username in the response payload.
- January 2026 commits `a942fe4` and `f5f5359` explicitly treat usernames as spoofable when making share-permission and arbitrary-upload decisions.
- The captured current master keeps token/message-type response admission but does not add a user-search expected-source binding.

## Bounded overlap result

Searches across official public issues, pull requests, commit history, and protocol material found adjacent discussions of malformed search results, ignored users, token tracking, connection spoofing, and payload-username compatibility. They did not surface a public item that states this cube's exact claim chain:

```text
user-mode expected set
+ allowed sequential token
+ PeerInit-derived claimed username
+ off-set handler acceptance
+ proposed expected-set filter
```

This is a bounded search result, not a novelty claim. More importantly, absence of a public duplicate would not repair the missing identity, attacker-capability, or impact evidence.

## Official references consulted

- Nicotine+ security policy
- Nicotine+ Soulseek protocol documentation
- Nicotine+ repository commit history
- Nicotine+ issue and pull-request search
