# Discovery path review page: tracker, LAN, predefined-host, and no-bootstrap branches interface spec

This page exists so four superficially similar connectivity setups stop pretending to mean the same thing:

- `Use tracker server`
- `Search LAN`
- `Use predefined hosts`
- `disable outside services`

All four affect peer discovery.
They do not create the same discovery contract.

## Operator question

> which discovery branch am I actually choosing here, what service contact does it require, and what reachability promise still remains blocked even if this branch is enabled?

## When this page must appear

Render whenever the operator is about to:

- disable tracker discovery
- disable LAN search in a topology that may still rely on it
- add or remove predefined hosts
- require peer finding to stay inside LAN only
- require discovery to work without contacting external discovery services
- diagnose a `peers not connecting` situation where multiple discovery rungs are plausible

## Fixed page order

1. **Branch chooser**
2. **What this branch requires**
3. **What this branch exposes**
4. **What this branch still does not prove**
5. **Safer weaker alternative**

## 1) Branch chooser

Offer mutually exclusive or explicitly combinable branches such as:

- `Tracker-assisted WAN discovery`
- `LAN-only discovery`
- `Predefined-host mesh`
- `Mixed discovery with fallback`
- `No external discovery services`
- `Abort and inspect current evidence`

The operator must be able to answer: **which discovery policy branch did I actually choose?**

## 2) What this branch requires

For the chosen branch, show minimum requirements:

- `Tracker-assisted WAN discovery` requires tracker reachability and publishes share-matching metadata to the tracker.
- `LAN-only discovery` requires multicast / broadcast visibility inside the target network.
- `Predefined-host mesh` requires accurate address:port knowledge on all peers and may still fail if direct reachability is blocked.
- `No external discovery services` requires that the product has some other provable peer-introduction basis; otherwise reachability is intentionally reduced.
- `Mixed discovery with fallback` requires the operator to accept that different peers may arrive through different origins at different times.

## 3) What this branch exposes

Show the data classes that leave the local trust boundary for this branch:

- tracker metadata only
- encrypted byte carriage possible later
- local multicast presence only
- manual address knowledge only
- no current outside-service contact

The operator must be able to answer: **what extra infrastructure knowledge am I authorizing by choosing this branch?**

## 4) What this branch still does not prove

Examples:

- enabling tracker does not prove direct transport will succeed
- enabling LAN search does not prove cross-subnet visibility
- entering predefined hosts does not prove the addresses are correct or reachable
- disabling tracker does not prove zero third-party contact if relay or link-landing still exists
- mixed discovery does not prove which branch will win for the next peer arrival

The product must say plainly when a branch is merely allowed, not yet witnessed.

## 5) Safer weaker alternative

Always show one weaker branch, for example:

- `Disable relay fallback but leave tracker discovery`
- `Use predefined hosts only for named peers`
- `Allow LAN discovery only on trusted interfaces`
- `Keep discovery unchanged; inspect route proof first`

## Commit rail

Example actions:

- `Commit tracker-assisted discovery`
- `Commit LAN-only policy`
- `Commit predefined-host branch`
- `Commit no-external-discovery policy`
- `Back out and gather more route evidence`

## What this page must never imply

It must never imply that these are the same:

- finding peers and transporting bytes
- disabling tracker and achieving total metadata isolation
- adding a predefined host and proving direct reachability
- seeing a peer once and preserving a durable discovery route forever
