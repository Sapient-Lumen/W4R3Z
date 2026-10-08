# Moderation quarantine allegation pressure

`moderationquarantine.py` models subjective policy capsules as local pressure. The capsule may be issued by a maintainer policy key, garden operator policy key, bridge operator, or user-selected policy source. It can warn, watch, deny, or freeze a scoped action.

The important guardrail:

> The capsule controls local side effects. It does not invalidate signed DHT records globally.

The surface checks:

- signature validity
- expiry/future time windows
- replayed capsules
- profile/service/scope/request/action/subject drift
- sequence rollback
- same-sequence forks
- previous-link mismatch
- family/path diversity for blocking decisions
- hard-negative pressure inside the capsule
- appeal/redress availability

This is the cube's answer to the authority tradeoff: official builds and public bridges may refuse keys, but the protocol core should not confuse refusal with universal truth.
