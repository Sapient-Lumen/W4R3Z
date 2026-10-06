# Host activation via rc.d + service jails (BSD-native orchestration)

DeriveBSD host activation must:
- be **atomic** (ZFS boot environments)
- be **auditable** (what services were enabled, with what knobs)
- minimize runtime blast radius (service jails where possible)

## rc.d as the activation backend
FreeBSD uses the rc.d framework (rc.subr) with configuration via rc.conf(5) and orchestration via service(8).
This is stable, deterministic, and well-documented.

DeriveBSD uses rc.d for:
- enabling/disabling host services for a generation
- launching/monitoring microVM instances as host “services”
- ensuring service start ordering is predictable

## Service jails (blast-radius reducer)
FreeBSD supports “service jails”: running services inside jails managed by the rc framework.
Service jails are configured via rc.conf/sysrc and managed via service(8), not jail(8).

DeriveBSD use:
- default: run DeriveBSD control-plane daemons in service jails when possible
- policy-gated: some services require networking privileges (`*_svcj_options=net_basic`), others remain host-root

## Activation flow (host generation)
1) Realize Plan → build closure + configs + rc knobs
2) Create ZFS boot environment (docs/69)
3) Write generation config into BE:
   - rc.conf fragments
   - rc.d scripts (or script snippets) for microVM instances
   - service-jail knobs where policy requires
4) Activate BE via bectl + reboot (default) OR controlled live switch (advanced)

All activation outputs are hashed and referenced in the boot manifest (docs/51).

Activation planning should also emit a **compiled service database** (`svcdb`) that captures dependencies, placement, and restart policy for diff/review and `derive explain` surfaces; see `docs/114-service-manifests-smf-lessons.md` (RFC-0082) and `docs/214-service-supervision-health-as-evidence.md` (RFC-0149).

Optionally, activation can also emit **activation capsets** for services that should run without ambient authority.
These capsets describe pre-opened, rights-minimized handles (listeners, state dirs, broker endpoints) that an activation broker can escrow across restarts.
See: `docs/196-capability-activation-and-escrow.md` (RFC-0131).

## Non-goals (v1)
- replacing rc.d with a new init system
- managing service jails via jail(8) (avoid conflicting sources of truth)
- “live mutate everything” without BE safety net

See RFC-0056 and ADR-0027.
References in `docs/32-curated-references.md`.

Last updated: 2026-02-24
