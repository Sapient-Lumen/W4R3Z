# Resource profiles: mapping to rctl + cpuset (host, jails, microVM processes)

DeriveBSD resource governance must be:
- deterministic
- auditable
- enforceable by OS primitives

FreeBSD provides:
- **rctl** subsystem + `rctl(8)` tooling (`rctl(4)`, `rctl.conf(5)`)
- **cpuset** tooling (`cpuset(1)`)

(see `docs/32-curated-references.md`)

## Model

A DeriveBSD `resource_profile` is a typed object in policy/Plan, e.g. (conceptual YAML):

```yaml
cpu: { cpuset: "0-3" }
mem: { max_rss: "2G" }
proc: { max_proc: 256 }
```

## Mapping rules (v1)

### cpuset
- Apply CPU affinity to:
  - the bhyve process for the microVM instance
  - build jail processes (optional)
- Record applied cpuset in runtime logs.

### rctl
- Apply RCTL rules to:
  - the microVM process tree (bhyve pid subject)
  - build jails (jail subject)
  - control-plane daemons (optional)

rctl rules can be applied at runtime and also loaded from `/etc/rctl.conf` (format described by `rctl.conf(5)`).

Important rctl baseline note:
- `rctl(4)` documents `kern.racct.enable` controlling whether resource accounting is enabled.

## Auditing invariants

- resource_profile_digest is part of Plan identity when policy says so
- every launch logs:
  - instance_id
  - applied cpuset
  - applied rctl rules (canonical text digest)

## Non-goals (v1)

- perfect per-VM IO accounting on all hardware paths
- automatically “best-effort” scaling without explicit policy (avoid hidden behavior)

Last updated: 2026-02-23
