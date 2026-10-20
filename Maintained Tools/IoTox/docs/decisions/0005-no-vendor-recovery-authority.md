# ADR 0005: No vendor device-reassignment authority

**Status:** accepted for rev0002

## Context

A vendor-held recovery key would make support convenient but would also make the vendor a permanent superior owner capable of reassigning customer devices. That contradicts the self-owned product thesis.

## Decision

IoTox will not hold, ship, or operate a key that can reassign customer device ownership.

Manufacturer keys may attest hardware model, provenance, or approved firmware. They must not authorize owner replacement. IoTox-operated bootstrap nodes, relays, update mirrors, or support systems likewise receive no ownership authority.

## Consequences

- Support cannot recover a lost recall phrase.
- Legal or operational pressure on IoTox cannot produce a universal reassignment action that the system does not contain.
- Hardware reclamation, where offered, must be a local factory-reset policy that erases the old ownership domain rather than revealing it.
- Owners carry the real responsibility and power associated with the recall phrase.
