# Compiled service database and bundles (s6-rc lessons)

DeriveBSD’s activation story can stay **FreeBSD-native** (`rc.d` scripts, service jails), but Nix pros and operators benefit from a higher-level *service state model*:

* explicit dependency graph
* offline analyzability (“what will start?”)
* bundles/targets (“bring up networking + fetch-domain + cache”)

## The lesson to steal

`s6-rc` treats service management as managing **machine state** from an offline-compiled database of services and dependencies. It also has the notion of *bundles* (named sets of services managed together).

Even if DeriveBSD does not adopt s6, the model is valuable:

> derive a **compiled service DB** from declarative inputs, and use rc.d only as a backend executor.

## DeriveBSD proposal

### Artifact: `svcdb`

From the runtime-source layer (`derive.unit` plus policy/profile inputs), derive a single **compiled service database** artifact:

* `svcdb` — service definitions, placement, dependency edges, restart policy, resource budget hints
* `svcdb.bundles` — named targets (e.g. `base`, `net`, `control-plane`, `workloads`)

Bind `svcdb.digest` into the Plan identity chain, so service topology is part of what you review and sign.
Bind it back to the reviewed source through `derive.unit.compile.receipt` rather than treating `svcdb` as a second hand-authored source.

Schema + examples live in `spec/svcdb.schema.json` and `spec/examples/svcdb.json`.

### Activation backend remains rc.d

`derive switch` translates `svcdb` transitions into:

* rc.d invocations
* service-jail lifecycle
* health gates (commit generation only if required bundles are healthy)

### Tooling UX

* `derive svc graph` — print/emit dependency graph
* `derive svc diff` — what changed in services/bundles between generations
* `derive svc why <service>` — show dependency reasons

## Why this is “tight” for DeriveBSD

This gives Nix-like introspection without importing Linux init systems:

* the **data model** is portable and auditable
* the **executor** is FreeBSD-native

## References

- s6-rc overview (compiled service database, offline inspection tooling): https://skarnet.org/software/s6-rc/overview.html
- s6-rc bundle tool (modifying bundles without recompiling): https://skarnet.org/software/s6-rc/s6-rc-bundle.html
- SMF overview (`smf(7)`): https://smartos.org/man/7/smf
- FreeBSD rc system overview (high-level article): https://klarasystems.com/articles/rc8-freebsd-services-and-automation/
- FreeBSD service jails (“automatic jailing of rc.d services”): https://www.freebsd.org/status/report-2024-04-2024-06/service-jails/

Last updated: 2026-03-08r229
