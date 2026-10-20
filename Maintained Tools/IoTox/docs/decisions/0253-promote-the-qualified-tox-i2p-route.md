# ADR 0253: Promote the qualified Tox/I2P route without changing its wire class

Status: accepted VM-qualified product route, 2026-08-29.

## Context

ADRs 0211–0219 and 0225–0229 constructed and qualified an actual I2P carriage path under the
deliberately non-product spelling `tox/i2p-construction`. The evidence now covers the exact-record
SOCKS-to-SAM adapter, canonical b32 naming, two distinct source-pinned i2pd routers, persistent
address-preserving service fronts, bounded c-toxcore establishment, two source-linked Sandwurm
guests, packet containment, router/front replacement, signed member-class admission, fail-closed
loss, and range-v1 payloads. The remaining distinction between that path and reserved `tox/i2p` was
only the product spelling.

Changing the already signed route-set class would create a migration without adding a security
boundary. Numeric network class 3, local-control route constraint 4, the I2P savedata path, and the
strict provider configuration already name the qualified construction.

## Decision

`tox/i2p` is the canonical VM-qualified product spelling for that exact route. It requires one
explicit numeric SOCKS endpoint plus explicit nonempty numeric bootstrap and TCP-relay records,
disables UDP/discovery/DHT announcements/hole punching/native DNS, suppresses compiled catalogs,
and has no native fallback. It continues to use `device.tox-i2p.toxsave`.

The signed route-set-v2 byte remains 3 and now renders canonically as `tox/i2p`. Local-control route
constraint byte 4 does the same. `tox/i2p-construction` remains accepted as a deprecated
reproduction alias and maps to those same numeric values and strict provider options. Existing
signed artifacts, savedata, and historical compact evidence need no rewrite. Historical evidence
retains its recorded construction label; verifiers do not relabel old receipts.

Add exact `client-tox-i2p` and `device-tox-i2p` NixOS configurations and a `tox-i2p` pair mode to the
Sandwurm runner, verifier, compact exporter, and operator wrapper. Promotion requires the production
spelling itself to pass the actual two-router/three-front baseline with both raw and secret-free
compact replay.

## Qualification

Compact proof `pair.btm5vwr9` passes. Two independent source-linked Cloud Hypervisor guests launch
the production spelling, report `Tox/I2P` and TCP, establish friendship and the canonical session,
and exchange text bilaterally. Both TAP captures contain zero native UDP, zero direct bootstrap
packets, and zero direct peer packets; every guest egress flow is TCP to the one numeric bridge
adapter. The topology binds three persistent I2P fronts and two i2pd routers. The 2.3 GiB private raw
root and 1.2 MiB compact root independently pass the strict verifier.

Exact hashes and reproduction commands are in
`docs/evidence/2026-08-29-sandwurm-tox-i2p-production.md`.

## Consequences

- IoTox now has three selectable Tox route classes: native, Tor, and VM-qualified I2P.
- No peer frame, feature bit, signature domain, numeric route class, savedata location, or authority
  rule changes.
- A named `fail-closed tox/i2p` sync pull and signed route member select the canonical class. The old
  construction text is input compatibility only and is not emitted for new artifacts.
- This proves fail-closed I2P carriage on this construction host and VM topology. It does not prove
  anonymity, resistance to traffic analysis, public-front uptime, operator diversity, physical-host
  diversity, broad records/time windows, fleet behavior, or a general I2P outproxy.
