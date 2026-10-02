# ADR 0252: Qualify one-source content-v2 on genuine native carriers

Status: accepted genuine-provider product gate, 2026-08-29.

## Context

ADR 0251 activated the content-v2 service only after complete Agent construction and persisted-graph
validation. Its strongest evidence still used mock toxcore. The next gate was deliberately narrow:
prove that two independent source-linked IoTox guests can publish, transfer, reconstruct, accept,
and explicitly activate the same paged content revision through genuine c-toxcore over both native
carrier forms. This gate must not silently become a claim about sparse sources, striping, restart,
or performance.

The first forced-TCP calibration reached bilateral synchronization authority at the controller's
240-second boundary. Both authority-ready records and the publisher declaration were durable, and
no guest failure existed, but the host had already classified the cell as timed out. The existing
service-update gate already uses a 480-second authority allowance for this class of slow route
construction.

## Decision

Add `sync-content` as a dedicated 4 MiB Sandwurm scenario. Both guests configure the namespace as
`content-v2`. The publisher requires a paged root manifest with four chunks, one page, and four
deduplicated objects and proves that the signed root resolves in its canonical CAS. The subscriber
requires negotiated bit 29, converges through the ordinary `sync-pull`, verifies reconstructed
whole-artifact and root-manifest CAS paths, and performs the ordinary exact-token `sync-activate`.
The publisher validates the subscriber's final generation, hashes, byte sizes, and content shape.

The host controller gives only `forced-tcp + sync-content` the 480-second synchronization-authority
allowance. Transfer, receipt, and total pair deadlines are unchanged. Compact export retains the
content-specific completion record, and strict replay requires its exact ordered fields to bind the
scenario shape to the pair manifest.

## Qualification

Two simultaneous source-linked Sandwurm microVMs passed on direct UDP and forced TCP. Both cells use
the same binary SHA-256, stable test-only identity baselines, c-toxcore 0.2.23, and libsodium 1.0.22.
Each performed one initial pull with zero failure and produced the same generation-1 signed HEAD,
4 MiB artifact digest, 272-byte paged root-manifest digest, and explicit activation. Both raw roots
and their 163,840-byte secret-free compact forms independently pass the strict verifier.

The retained evidence and exact hashes are recorded in
`docs/evidence/2026-08-29-sandwurm-sync-content.md`.

## Consequences

- The one-source, one-lane content-v2 primary-carrier path is now qualified through genuine
  c-toxcore on native UDP and forced TCP. It is no longer merely a deterministic/mock-provider path.
- This does not change feature negotiation, framing, authority, HEAD-last acceptance, or explicit
  activation. Feature bit 29 still describes only the bounded path constructed by ADR 0251.
- A slow authority handshake is not confused with failed content transfer, but only the observed
  forced-TCP content scenario receives the larger construction allowance.
- Sparse-availability consumption, multiple sources, auxiliary carriers, selected-source loss,
  daemon restart, performance advantage, arbitrary filesystem/power faults, and physical-host
  diversity remain unqualified.
