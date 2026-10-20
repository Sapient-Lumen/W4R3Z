# ADR 0152: Qualify provider savedata before rolling network upgrades

Date: 2026-08-24

Status: accepted

## Context

IoTox statically links one pinned c-toxcore provider. A provider update can therefore change two
separate boundaries: durable c-toxcore savedata and live wire interoperability during a rolling
deployment. The current official pin is 0.2.23; the immediately preceding stable release is 0.2.22.
IoTox itself did not ship on 0.2.22, so reconstructing an old IoTox binary would invent a product
history. The honest durable input is savedata emitted by the exact previous provider.

## Decision

- Pin the official c-toxcore 0.2.22 release archive as a qualification-only input. It is not linked
  into the product or listed as a product SBOM component.
- Build one warnings-as-errors fixture against exact 0.2.22 source and another against the current
  exact 0.2.23 `iotox-file-rr1` source. Both use the product-pinned libsodium and the exact cmp gitlink
  shared by the two tags.
- Create two disposable 0.2.22 savedata identities with distinct keys and profiles, add their public
  keys as mutual friends, and require 0.2.23 to preserve address, public key, name, status message,
  status, friend count, and friend key exactly.
- Rewrite both profiles through 0.2.23 and require both versions to read the same semantic snapshot.
  Backward readability is evidence, not permission to downgrade a distributed IoTox binary.
- Start the actual source-linked IoTox product once for each prior-provider profile. Preserve its
  separately generated IoTox device identity, load the old Tox address/profile/friendship through the
  real Agent, stop cleanly, and require both provider fixtures to read the IoTox-written state.
- Require both provider fixtures to reject a bounded malformed savedata input.
- Emit only versions, source digests, booleans, counts, and savedata sizes. Disposable keys, addresses,
  profiles, and savedata bytes never enter the derivation output. Rebuilding the check must reproduce
  the exact receipt bytes.

## Consequences

The flake now rejects a regression in the concrete 0.2.22-to-0.2.23 durable provider boundary. This
is stronger than testing a same-version restart and avoids weakening IoTox's runtime ABI floor: the
official binary remains statically pinned to 0.2.23 and cannot dynamically fall back to 0.2.22.

This gate does not prove a live old/new mixed-provider connection, public-network rolling deployment,
future 0.2.24 compatibility, all historical savedata, corrupted-but-parseable semantic behavior, or
safe security rollback. A two-guest Sandwurm mixed-provider route cell remains the final M3 provider
upgrade gate.
