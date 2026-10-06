# Capsicum/Casper hardening plan

DeriveBSD control plane daemons should reduce ambient authority.
FreeBSD provides:
- **Capsicum** (capability mode)
- **Casper** (brokered services for capability-mode programs)

Primary refs:
- Capsicum overview + invariants: https://man.freebsd.org/capsicum%284%29
- Casper service broker API: https://man.freebsd.org/cgi/man.cgi?query=libcasper&sektion=3

## v1 plan

Capsicum’s core idea: after `cap_enter(2)` the process loses access to global namespaces (filesystem lookup, process IDs, etc.) and can only use explicitly delegated rights (file descriptors / memory mappings). Capability mode is inherited by children and cannot be cleared. (ref: `capsicum(4)`)

Casper complements this by exposing specific OS services (e.g. DNS, syslog) through a broker, so capability-mode programs can still “ask for” narrowly scoped services without regaining ambient authority. (ref: `libcasper(3)`)


## Networking note

Capsicum capability mode does **not** automatically remove network egress as ambient authority.
For DeriveBSD’s approach (brokered egress grants + receipts, DNS mediation), see `201-network-egress-as-capability.md`.

Casper’s base system includes `system.dns` (usable via `cap_dns`) which is a practical adapter for DNS-in-capability-mode.

### Daemon-by-daemon hardening sketch

- `derive-vmmd` (microVM control plane)
  - **Before `cap_enter`**: open only the *exact* bundle/store paths needed to validate + launch; open the control socket(s) it will serve; pre-open log destinations.
  - **After `cap_enter`**: all VM lifecycle operations must be expressed through pre-opened handles + explicit helper processes.

- `derive-fetchd` (fetch-only networked component)
  - **Before `cap_enter`**: open destination dirs + CA bundle; open cache index DB; open a minimal set of sockets required for the fetch loop.
  - **Casper**: consider using Casper’s DNS service rather than ambient resolver state.
  - **After `cap_enter`**: no filesystem discovery; only write into pre-opened dirs.

- `derive-stored` (store verification + GC)
  - **Before `cap_enter`**: open store root(s), verification temp dir, and any required device nodes.
  - **After `cap_enter`**: operate only on open dataset/file handles; refuse path strings.

### Engineering rules (keep it ergonomic)

- **“Pre-open handle” workflow by default**: daemons accept file descriptors (or cap descriptors) instead of paths wherever possible.
- **Narrow rights early**: apply `cap_rights_limit(2)`, `cap_ioctls_limit(2)`, etc. before entering capability mode.
- **Test harness**: each daemon has a CI mode that runs in capability mode and proves it can still perform required operations.
- **Debug escape hatch** (policy-gated): allow temporarily disabling Capsicum for debugging, but require emitting an explicit “ambient-authority enabled” evidence object.

### When pre-open isn’t enough (portals)

Some workflows need *dynamic* access after capability mode is entered (e.g., user-chosen files, incident-driven exports, late plugin loads).
DeriveBSD should avoid “just keep ambient authority” by standardizing a brokered-grant mechanism:

- Portals / powerbox broker (typed requests → policy → narrow grants + evidence): `docs/179-portals-and-powerbox.md`
- Capability-mode dynamic linking strategy (avoid dlopen backsliding): `docs/180-capability-mode-dynamic-linking.md`

See RFC-0028, RFC-0114, RFC-0115.
Last updated: 2026-02-24
