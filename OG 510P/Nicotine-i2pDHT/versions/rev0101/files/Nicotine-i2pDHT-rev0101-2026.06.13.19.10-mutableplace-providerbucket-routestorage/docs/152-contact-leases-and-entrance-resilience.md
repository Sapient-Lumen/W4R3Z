# Contact leases and entrance resilience

A contact card is self-signed reachability. A contact lease is local memory about whether this node should keep using that card.

The lease layer exists because entrance growth is seductive. A network that wants rapid DHT adoption will accept contacts through direct invites, gardens, friends, rooms, bridges, cached last-good contacts, and legacy network side channels. That is exactly where replayed cards, stale cards, captured introducers, and monoculture enter.

rev0018 adds:

```text
ContactLeaseObservation
ContactLease
ContactLeaseBook
ContactPortfolioReport
```

A newer card can renew an older card only if it links to the cached `previous_card_hash`, unless local policy disables that requirement. This is a deliberately strict guess: renewal gaps are not proof of malice, but they are a cheap place to preserve evidence before stale or split-view contact histories become normal.

Portfolio selection is also capped by introducer family and checked for entrance-channel diversity. Gardens and seed gates are preferred when they are present, but they do not bypass diversity checks.

The local rule:

```text
A valid contact card is not automatically a good bootstrap entrance.
```
