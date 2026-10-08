# Supernodes that give

We do not need to fear the word `supernode`.  We need to define it correctly.

A DHT above I2P will naturally have resource-rich nodes and resource-poor nodes.  Pretending otherwise would make the protocol worse.  The goal is not to abolish high-capacity nodes; the goal is to prevent high-capacity nodes from becoming mandatory authorities.

## Allowed supernode powers

Garden supernodes may:

- answer DHT queries;
- store records within advertised budgets;
- reprovide provider and mutable records;
- maintain large routing tables;
- help bootstrap new nodes;
- run sentinel checks;
- cache hot-key breadcrumbs;
- accept delegated wake-courier records;
- publish signed capability and refusal statements;
- expose diagnostics to their operator.

## Forbidden supernode powers

Garden supernodes must not:

- decide global truth;
- become the only bootstrap path;
- require account registration;
- issue mandatory reputation;
- unilaterally blacklist for the network;
- hold private keys for clients;
- require clients to reveal full inventories;
- store unbounded content by default;
- make a lookup acceptable without path/quorum checks.

## The helping-supernode pattern

```text
capability_ad -> local selection -> bounded service -> signed receipt -> local scoring
```

No global promotion ceremony is needed.  A garden says what it can donate.  Peers try it.  Peers remember what happened.

## Learning from I2P without copying it

I2P floodfill routers show that a subset of higher-capacity routers can provide special DHT-like storage/query services while remaining untrusted and changing over time.  I2P also documents hard problems: malicious floodfills, partial keyspace capture, bootstrap attacks, and lookup metadata leakage.  The garden layer should borrow the honesty about roles and the peer-profile idea, but should not copy floodfill's authority shape into the application DHT.

## Garden anti-capture rule

Every garden feature should include an anti-capture question:

```text
What happens if the user's three favorite gardens are malicious?
```

The answer should be one of:

- cross-check with disjoint non-garden paths;
- use multiple gardens selected by different local criteria;
- decay and exploration force replacement;
- only accept signed records validated by the publisher;
- expose a warning, not a truth decision;
- fail closed for high-risk metadata modes.

## Operator stickiness

Garden nodes should have an operator-facing dashboard someday:

```text
You served 18,230 lookups.
You refreshed 91,400 provider records.
You repaired 312 stale mutable heads.
You refused 47 overload batches before dropping traffic.
You helped 88 new nodes bootstrap.
Your best-served regions were 0x2a, 0x2b, 0xa1.
```

This is not vanity.  It is social ergonomics for contribution.
