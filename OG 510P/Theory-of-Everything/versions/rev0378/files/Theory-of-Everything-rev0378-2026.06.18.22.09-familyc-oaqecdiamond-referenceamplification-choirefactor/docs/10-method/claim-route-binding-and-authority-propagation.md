# Claim-route binding and authority propagation

## Purpose

The archive now treats broad claim language as a downstream effect of executable bindings, not as free prose. `CLAIM-ROUTE-BINDING-LEDGER.json` states which routes, carriers, acquisition protocols, and controlling ledgers may support each high-risk claim or open question.

## Propagation rule

A claim inherits the most restrictive surviving ceiling among:

```text
route authority state
route promotion ceiling
public-record carrier maximum credit
acquisition protocol maximum effect
negative-control state
empirical-delta state effect
promotion gate
observed-sector obligation
claim binding rollback rule
```

A broad claim cannot propagate upward from a release summary, generated mirror, route table, DOI, repository pointer, or forecast. It can only propagate from the executable row bundle that owns the target claim.

## Bindings added in rev0263

The current binding rows cover:

- `OQ-0057`: candidate-native identifiability across all route rows;
- `OQ-0058`: quotient, duality, frame, and candidate-identity adjudication;
- `OQ-0059`: observed-sector recovery;
- `OQ-0060`: public-record carrier and acquisition closure;
- `CL-0169`: low-energy and strong-field discriminator discipline;
- `CL-0175`: forecast artifact discipline.

## Practical consequence

When a future source arrives, the archive should not first ask whether it is exciting. It should ask:

1. Which route row does it touch?
2. Which public carrier holds the record?
3. Which acquisition protocol produced or replays it?
4. Which claim binding allows wording to change?
5. What rollback fires if the carrier, protocol, or replay fails?

If those answers are missing, the source can remain useful background or navigation, but it cannot change route authority.
