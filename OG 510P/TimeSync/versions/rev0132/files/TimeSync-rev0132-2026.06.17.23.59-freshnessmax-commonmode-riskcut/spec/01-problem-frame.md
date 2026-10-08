# 01 — Problem frame

## Timing systems are plural

Time synchronization spans general computing, distributed coordination, financial timestamping, telecom and precision networking, electric power and other critical infrastructure, and degraded local operation. One protocol shape cannot honestly capture every operational, regulatory, and resilience requirement.

## Timing trust is multi-dimensional

A useful state needs to separate at least these dimensions:

```text
authenticity
correctness or uncertainty
traceability or source relationship
freshness
operating regime
source posture
downstream applicability
```

Conflating these dimensions produces false confidence. For example, an authenticated source can be wrong, a locally coherent clock can be untraceable, and a degraded clock can remain useful for some applications but not for others.

## Timing is not only packet exchange

Timing systems also involve source selection, source diversity, holdover, failover, fault detection, degraded operation, relay/aggregation, recovery, and governance. TimeSync therefore distinguishes a thin wire claim from richer local assessed state.

## Two tracks remain useful

```text
Integration track: work with current protocols, profiles, and institutions.
Greenfield track: define the smallest cleaner substrate from first principles.
```

Both tracks use the same pressure tests. The integration track prevents fantasy. The greenfield track prevents being trapped by incumbent protocol layouts.

## Current compact answer

The archive now stabilizes around a six-field TimeState, surrounded by profile-scoped obligations, tiny extension hooks, request/result accounting, boundary context, and lifecycle/current-policy handling.
