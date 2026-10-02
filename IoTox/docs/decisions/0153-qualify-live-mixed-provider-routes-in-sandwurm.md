# ADR 0153: Qualify live mixed-provider routes in Sandwurm

Date: 2026-08-24

Status: accepted

## Context

ADR 0152 qualified durable c-toxcore state across the exact 0.2.22 to 0.2.23 boundary, including
real-product load and rewrite. Durable readability alone does not prove that an old and current
provider can communicate during a rolling deployment. IoTox did not ship on 0.2.22, so inventing an
old IoTox binary would create false product history. The remaining honest wire boundary is the exact
old provider against the exact current provider in the project's real two-guest laboratory.

## Decision

- Extend the qualification-only warnings-as-errors fixtures with one bounded live exchange command.
  It loads existing savedata, disables IPv6 and local discovery, selects direct UDP or forced TCP,
  bootstraps through the pinned laboratory fixture, requires the exact friend connection kind, and
  sends and receives distinct fixed messages.
- In two simultaneous Sandwurm KVM guests, create both distinct identities and their mutual
  friendships through exact c-toxcore 0.2.22. Keep the client live on 0.2.22 and open the device
  savedata and live connection with exact 0.2.23.
- Run the matrix over both direct UDP and forced TCP. The peer connection, rather than the provider's
  global DHT status, determines the route: c-toxcore may report a TCP bootstrap-facing self status
  while an exact friend already communicates over direct UDP.
- Require each role to send its fixed message and receive the peer's fixed message. After the live
  exchange, rewrite savedata through the role's live provider and require both 0.2.22 and 0.2.23 to
  read an identical semantic snapshot.
- Retain only versions, official source digests, fixture binary digests, route, booleans, savedata
  size, KVM truth, Sandwurm launch bindings, and monotonic harness duration. Tox keys, messages,
  savedata, bootstrap secret state, guest disks, and runtime journals remain private and are omitted
  from the strictly verified compact export.
- Keep 0.2.22 qualification-only. Passing backward readability and live interoperability never
  authorizes automatic provider downgrade.

## Consequences

M3 now has a concrete live rolling boundary for the current pin: 0.2.22 client to 0.2.23 device over
the founding-machine two-Sandwurm-guest direct-UDP and forced-TCP topology. Combined with ADR 0152,
the same transition is qualified for durable state, real current-product load, live wire exchange,
and post-exchange cross-version readability.

This does not prove a public-network or production-fleet rollout, an old IoTox application protocol,
all historical savedata, downgrade security, a future provider pin, NAT diversity, or compatibility
in the reverse deployment direction. Every provider-pin change must repeat the durable and live
decisions against its actual predecessor before release.
