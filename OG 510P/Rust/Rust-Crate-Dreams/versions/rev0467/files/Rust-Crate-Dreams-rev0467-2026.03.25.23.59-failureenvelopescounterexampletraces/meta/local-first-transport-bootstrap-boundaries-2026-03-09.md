# Local-first transport & bootstrap boundaries — 2026-03-09

This note exists to stop future passes from collapsing **sync transport**, **bootstrap convenience**, **durable identity**, and **authorization** into one fuzzy “peer connection” story.

## Main judgment

The sharper missing value in **P-0076 Local-first Sync Kit** is not merely “pick a P2P library”.
It is a **reviewable transport/bootstrap contract** above existing substrate.

Three current facts matter:

1. Automerge’s sync protocol assumes a **reliable in-order stream** between two peers.
2. iroh is strong substrate for local-first networking, but it makes protocol/version routing, relay fallback, and bootstrap choices explicit rather than magical.
3. MLS / OpenMLS help with **group key state**, but they do **not** make bootstrap tickets or transport handles into durable authorization truth.

## The boundary that future passes must preserve

Treat these as separate layers:

1. **document sync semantics** — e.g. Automerge sync messages and convergence assumptions,
2. **transport session semantics** — direct vs relayed path, ordered stream assumptions, protocol version, retry/failure classes,
3. **bootstrap handle semantics** — tickets, invite links, endpoint IDs, or coordination-server references,
4. **durable replica / member identity** — the identity the app actually reasons about over time,
5. **authorization / membership truth** — who is allowed to participate, under which epoch, after which removal or rotation.

A good crate should export these separately.
A bad crate will stuff them all into one “connected peer” field and make support, privacy review, and incident triage much harder.

## Why this matters now

### Automerge does not make transport truth disappear
Automerge is network-agnostic and its sync protocol assumes a reliable in-order stream.
That is a strength, but it means a higher-level product kit must still record the transport guarantees it relied on.
If two incident bundles used materially different transport assumptions, the crate should be allowed to say they are only **partially comparable**.

### iroh is useful precisely because it surfaces transport and bootstrap choices
Current iroh docs make several boundaries unusually clear:

- protocols are selected via **ALPN** and routed explicitly,
- relays are a **fallback** when direct paths are unavailable,
- public relays are suitable for **development/testing**, while production should use dedicated relays,
- tickets are a **serializable convenience token**, not a durable identity primitive.

That means a worthy local-first crate should record:

- protocol ID / version,
- direct vs relay path,
- relay class (`public`, `dedicated`, `self_hosted`, `none`),
- bootstrap method (`ticket`, `endpoint_id`, `directory`, `manual`),
- and any caveat that makes two sessions not directly comparable.

### Tickets are handy, but dangerous to treat as durable truth
Current iroh tickets pack endpoint addressing plus optional application-specific data.
They are useful for QR/bootstrap flows, but they can:

- expose IP addresses,
- be reused,
- go stale,
- and in application-specific designs, accidentally carry capability-like secrets.

So future local-first work in this archive should treat raw tickets as:

- **bootstrap material**,
- normally **redacted** from support bundles,
- and definitely **not** the long-term identity or membership record.

## What this means for P-0076

Read the transport/bootstrap lane of **P-0076** as:

> transport profile → bootstrap method → session receipt → comparability caveat → redacted bundle view

That is stronger than either:

- “just use iroh”, or
- “tickets/links/invites are the same as authorization”.

## Working rule

When touching local-first work in this archive, do **not** collapse:

- transport guarantees,
- relay path behavior,
- bootstrap convenience tokens,
- durable replica identity,
- and group membership / revocation truth

into one fake “peer connected” claim.

Future passes should prefer:

- session receipts with explicit path and bootstrap fields,
- redaction rules for bootstrap handles,
- same-user versus shared-group profiles with different expectations,
- and honest `not-comparable` outputs when two sessions used different transport or bootstrap assumptions.

## Sources

- https://automerge.org/automerge/automerge/sync/index.html
- https://automerge.org/docs/hello/
- https://docs.iroh.computer/what-is-iroh
- https://docs.iroh.computer/concepts/protocols
- https://docs.iroh.computer/protocols/automerge
- https://docs.iroh.computer/concepts/relays
- https://docs.iroh.computer/concepts/tickets
- https://datatracker.ietf.org/doc/rfc9420/
- https://github.com/openmls/openmls
