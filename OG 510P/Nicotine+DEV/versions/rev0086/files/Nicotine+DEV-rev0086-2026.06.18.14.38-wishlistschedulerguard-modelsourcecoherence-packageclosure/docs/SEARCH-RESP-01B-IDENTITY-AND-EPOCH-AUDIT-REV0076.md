# SEARCH-RESP-01B identity and request-epoch audit — rev0076

## Audit question

Can a buddy-search response be safely admitted by checking that its username belongs to a snapshot of buddies captured when the search was sent?

The answer is not yet. The check is mechanically implementable, but the old packet collapsed identity, authorization, recipient scope, and time into one tuple.

## Four distinct values

| Value | Origin | What it can prove | What it cannot prove |
|---|---|---|---|
| Search token | local search allocation, then carried on the wire | correlation with an allowed local search | peer account identity or recipient membership |
| Request recipient set | local buddy list at some send time | intended fan-out for one defined epoch | who owns a later socket or late reply |
| Connection username | peer connection `PeerInit` claim | the name under which this connection is tracked | server-authenticated ownership of that name |
| Response body username | `FileSearchResponse` payload | what the payload says | reliable identity; old Museek clients can send it incorrectly |

Local buddy/trusted share permission is a fifth, separate value. It is evaluated on incoming search requests, not on incoming search results.

## Counterexample to authentication interpretation

The executable identity test constructs wire `PeerInit` data with `init_user="buddy_a"`, parses it through the network message path, attaches the resulting connection username to a `FileSearchResponse`, and sends it through the historical guard. The guard accepts it because the claimed name is in the snapshot.

This deliberately does not claim that an attacker can complete every surrounding network step. It proves the narrower and decisive fact that the guard's input is a claim, not cryptographic or server-mediated authentication.

## Counterexample to timeless-snapshot interpretation

A search object can outlive one send operation. On master, Search Again looks up the existing search by token and sends it again. Current behavior resolves the buddy list at send time. The historical patch resolves it only at initial creation.

That creates at least two epochs:

```text
epoch 1: token T sent to {removed_buddy, staying_buddy}
epoch 2: token T resent to {staying_buddy, new_buddy}
```

A single `search.users` tuple cannot represent both without choosing a late-response policy. Freezing epoch 1 breaks current targeting. Replacing with epoch 2 can reject a legitimate late epoch-1 result. Taking the union preserves late results but makes removed names remain in scope. The rev0040 packet specifies none of these tradeoffs.

## Claim ladder

| Claim | Rev0076 result |
|---|---|
| Current supported branch has no buddy recipient-set admission check | Confirmed |
| rev0040 rejects off-snapshot claimed names when a snapshot is present | Confirmed |
| checked name is an authenticated buddy identity | Refuted as an interpretation of the available value |
| accepting a result grants access to local buddy/trusted shares | Refuted for this handler path |
| unrelated peers can practically inject accepted results | Not established |
| the behavior has material security impact | Not established |
| rev0040 preserves Search Again semantics | Contradicted on the master resend counterexample |
| a safe patch is selected | No |

## Disposition

Keep this packet open as request-epoch and compatibility research. Do not route it privately as a vulnerability on present evidence, and do not publish the historical patch as a ready fix.
