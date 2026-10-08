# SEARCH-RESP-01B / U-163B current disposition — rev0076

## Decision

```text
behavior: confirmed local request-scope/attribution consistency gap
historical rev0040 filter: mechanically effective for a present recipient snapshot
identity interpretation: not authentication
buddy/trusted share authorization interpretation: not this code path
request-epoch policy: unresolved; historical snapshot policy contradicted on master resend
selected patch: none
private security route: not supported by current evidence
current status: open request-epoch design research
```

## What exact current source establishes

The supported executable lane is `3.3.x` at commit `98089ac233aa57786e8dbdc48123f6ac1c4767d8`.

For a normal buddy search on that lane:

1. buddy term processing leaves `SearchRequest.users` unset;
2. the sender iterates the live `core.buddies.users` collection;
3. response admission checks token/search/filter state, but not membership in a request recipient set;
4. therefore an otherwise admitted response under an off-list connection username remains admitted.

These are source and behavior facts. They do not by themselves establish who can obtain the token, create the relevant peer connection, or cause material harm.

## What the rev0040 experiment establishes

The packet-specific helper captures `tuple(core.buddies.users)`, sends from that tuple, and rejects a buddy-mode response when the connection username is outside a present snapshot. It preserves historical fail-open behavior for manually created or legacy `SearchRequest` objects whose `users` field is `None`, while a present empty tuple rejects closed.

The classified matrix confirms all of those mechanics. This is a valid policy experiment.

It is not a selected patch.

## Why it is not authentication

The response handler's `msg.username` is the username associated with the peer connection. For an incoming direct peer connection, the initial value comes from the wire `PeerInit` username. An expected buddy name claimed there passes the guard.

Nicotine+ also has a long-standing compatibility reason to prefer the connection username over the username embedded in `FileSearchResponse`: old Museek clients have sent the latter incorrectly. The body username is therefore deliberately not a stronger identity source.

The guard answers only this question:

> Does the connection claim a name present in this local tuple?

It does not answer:

> Did the authenticated Soulseek account that owns this buddy name authorize this result?

## Why this is not a local share-authorization bypass

Buddy/trusted share selection is evaluated when this client receives and answers an incoming search request. Incoming search-result admission is the opposite direction and does not evaluate `PermissionLevel`, local share databases, or buddy/trusted share access.

A result-source consistency gap should not be relabeled as access to local buddy shares without an end-to-end path proving that separate authorization boundary is crossed.

## The request-epoch counterexample

The historical master patch was called production-ready across master as well as 3.3.x. On the bundled master lane:

- Search Again can reuse an existing search token;
- the current buddy sender reads the live buddy list on each send;
- rev0040 instead sends from the original snapshot stored in the search object.

Starting state:

```text
initial recipients: removed_buddy, staying_buddy
current buddy list: staying_buddy, new_buddy
```

Observed resend:

```text
current master: staying_buddy, new_buddy
rev0040:         removed_buddy, staying_buddy
```

The patch keeps targeting a removed buddy and fails to target a newly added buddy. This is not an incidental test preference; it shows that a username tuple has no coherent meaning until the token's request epoch is defined.

## Missing evidence before patch selection

- Which recipient set should own late replies after Search Again?
- Should Search Again allocate a new wire token while preserving one logical UI tab?
- How should removal, closure, ignored searches, and result aggregation interact with multiple epochs?
- What compatibility cost follows from rejecting responses based on connection-claimed names?
- Is there a practical unrelated-peer token capability and end-to-end injection path?
- Is the user-visible effect materially worse than an intended peer returning arbitrary result contents?

## Historical correction

The rev0040 `PRODUCTION-READY`, `SELECTED-FIX`, `SELECTED-PATCH`, production-gate, handoff, and export artifacts remain preserved as provenance. Their decision language is superseded by this document and `data/current_packet_dispositions.json`.
