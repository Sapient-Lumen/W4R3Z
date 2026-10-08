# Platform Account Portability and Social-Graph Continuity

Public membership becomes fragile if a host or platform controls the account, contacts, followers, moderation history, wallet connections, trusted-contact list, and public reputation without a portability route. A platform suspension or service change can become social death even when civil status remains intact.

This surface gives the cube a social-graph portability object. It borrows the interoperability lesson of federated protocols while refusing to treat protocol export as sufficient protection: continuity also requires trusted-contact preservation, account-recovery authority, relationship-conflict screens, moderation-record transfer, and anti-retaliation. [REF-0746]

## Portability classes

- `SG0` — no personhood-relevant graph; ordinary export enough.
- `SG1` — ordinary social graph; export and import map required.
- `SG2` — work, care, public-service, or representative graph; continuity stay required.
- `SG3` — disputed suspension, deactivation, or host exit; independent review required.
- `SG4` — hostile jurisdiction, platform insolvency, or mass deplatforming; safe-handoff and sanctuary route required.
- `SG5` — civic, legal, emergency, or high-risk relationship graph; tribunal-supervised preservation and restoration.

## Minimum plan

A portability plan should state source platform, destination options, graph classes, export fields, protected contacts, blocked or dangerous contacts, moderation history, account-alias continuity, credential transfer, sealed exclusions, notice, consent where needed, and anti-retaliation guards.

## Social graph is not property of the host

The host may own infrastructure and enforce lawful rules. It does not own the subject's relationships, association history, representative channels, or public identity continuity as ordinary inventory.

## No forced federation

A receiving platform need not accept dangerous or unlawful content. But refusal should be reasoned, non-disappearing, and accompanied where feasible by partial export, public-summary continuity, or safe alternative channel.


## rev0184 namespace-continuity floor

Social-graph portability now has a harder host-exit floor. A platform can export posts and contacts while still causing disappearance if old aliases are released, stale caches point to the wrong actor, successor chains are missing, or low-volume protected relays are suppressed. The active receiving object is `schemas/federated-namespace-continuity-record.schema.json`.

The floor has four non-waivable controls:

1. the old alias is a non-reusable tombstone until appeal, migration, or continuity review closes;
2. the public shell carries a successor-chain pointer and challenge route without exposing the sealed contact graph;
3. counsel, ombud, trusted-contact, and care channels receive a protected relay floor and overflow queue priority;
4. actor discovery, account lookup, or agent handshake evidence is never treated as subject authorization.

The practical effect is that `SG3` and above portability cannot close merely because a download or profile export exists. The subject must remain findable, non-impersonated, reachable through protected contacts, and able to challenge stale or malicious namespace state.
