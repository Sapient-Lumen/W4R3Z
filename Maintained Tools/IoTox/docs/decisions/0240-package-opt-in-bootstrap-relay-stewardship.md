# ADR 0240: Package opt-in bootstrap/relay stewardship

Status: accepted with NixOS VM qualification, 2026-08-29.

## Context

M8 requires a way for owners to contribute useful Tox bootstrap and TCP-relay capacity without
turning IoTox into mandatory infrastructure. The repository already source-pinned c-toxcore's sample
`DHT_bootstrap` for Sandwurm qualification, but it had no deployment contract, state ceremony,
resource boundary, firewall default, or reproducible service test. Telling operators to run the lab
binary by hand would create private key files in arbitrary working directories and leave the
stewardship promise unverifiable.

## Decision

- Export `nixosModules.toxBootstrap`. Import is inert. Enablement requires an explicit package and
  never downloads or selects a node catalog.
- Package the pinned c-toxcore 0.2.23 daemon with exactly one unprivileged TCP relay port, 33445;
  remove the sample listeners on 443/3389 and its unconditional misleading initialization error.
  UDP bootstrap and TCP relay use the same fixed port.
- Run under a systemd `DynamicUser` in a mode-0700 persistent state directory. Refuse symlinked,
  non-regular, wrongly sized, or non-0600 key/ID state before process start.
- Keep the host firewall closed by default. Explicit `openFirewall` opens TCP and UDP 33445 only.
  Router, NAT, provider-firewall, DNS, bandwidth, and public-catalog policy stay outside the module.
- Apply an empty capability set, `NoNewPrivileges`, private device/tmp views, read-only system
  protection, namespace/address-family restrictions, a descriptor ceiling, and operator-configurable
  memory/CPU/task ceilings. These reduce blast radius; they are not availability or DDoS claims.
- Treat the daemon key only as continuity for a reachability record. It grants no IoTox authority.
  Publish endpoints out of band, back up the key/ID pair offline, rotate explicitly, and never create
  an IoTox-run account, reassignment key, required endpoint, or silently enrolled community list.

## Qualification

`checks.x86_64-linux.toxBootstrapServiceTest` boots the service in a Sandwurm-compatible NixOS/KVM
test, observes TCP and UDP 33445, verifies the state directory and exact 64-byte mode-0600 key/ID
records, restarts the daemon, compares both SHA-256 values byte for byte, and checks `DynamicUser`,
`MemoryMax`, `TasksMax`, and explicit firewall rules. The operator procedure and nonclaims are frozen
in `docs/bootstrap-relay-operations.md`.

## Consequences

An owner can reproducibly contribute capacity without delegating device ownership or depending on
IoTox infrastructure. Service identity survives ordinary daemon restart and the deployment surface
is reviewable as Nix code.

The gate is local. It does not establish public reachability, uptime, abuse resistance, NAT behavior,
geographic/operator diversity, a mutable public-node catalog, or an IoTox service-level commitment.
Those remain external operational evidence, not facts a VM can manufacture.
