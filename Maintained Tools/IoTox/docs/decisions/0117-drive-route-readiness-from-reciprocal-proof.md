# ADR 0117: drive route readiness from reciprocal proof

Status: accepted

Date: 2026-08-21

## Decision

When route workers are explicitly enabled, Agent construction signs the already authenticated local
route set and installs a narrow binding factory plus the existing sodium verifier before auxiliary
networking begins. No new signing key or trust root is introduced.

On each bounded protocol service cycle the Agent derives remote route trust only from connected,
transcript-confirmed primary sessions whose stable principal is currently authorized by the local
authority ledger. The primary authority snapshot and protocol snapshot must agree on friend number,
transport public key, and online epoch. That exact primary peer Tox key becomes the required remote
route-set coordinator key.

A local worker moves from `connecting` through `authenticated` to `ready` only after its local
binding was accepted by transport and a reciprocal binding passed the registry from ADR 0115. Loss
of reciprocal authentication returns an authenticated or ready member to `connecting`, clears all
admitted work, and records an authentication failure without consuming the transport restart budget.
Transport recovery remains a separate lifecycle and budget.

## Consequences

The deterministic provider now exercises the whole primary-authority plus auxiliary-binding path and
observes a nonzero worker incarnation reach `ready`. A foreign self-signed inventory, mismatched
primary coordinator, stale authority epoch, missing local send, or absent reciprocal proof cannot
advance lifecycle state. Ordinary single-route operation remains unchanged.

No product scheduler consumes ready routes yet. Future work admission must reconcile current primary
authority at its own effect boundary rather than treating the periodic projection as an irrevocable
authorization lease. Genuine two-guest Sandwurm route loss and restart qualification remains separate
from this deterministic implementation proof.
